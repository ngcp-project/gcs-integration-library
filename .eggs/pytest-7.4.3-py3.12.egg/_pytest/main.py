"""Core implementation of the testing process: init, session, runtest loop."""

import argparse
import dataclasses
import fnmatch
import functools
import importlib
import os
import sys
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import (
	TYPE_CHECKING,
	Union,
)

import _pytest._code
from _pytest import nodes
from _pytest.compat import final, overload
from _pytest.config import (
	Config,
	ExitCode,
	PytestPluginManager,
	UsageError,
	directory_arg,
	hookimpl,
)
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureManager
from _pytest.outcomes import exit
from _pytest.pathlib import absolutepath, bestrelpath, fnmatch_ex, safe_exists, visit
from _pytest.reports import CollectReport, TestReport
from _pytest.runner import SetupState, collect_one_node

if TYPE_CHECKING:
	from typing import Literal


def pytest_addoption(parser: Parser) -> None:
	parser.addini(
		"norecursedirs",
		"Directory patterns to avoid for recursion",
		type="args",
		default=[
			"*.egg",
			".*",
			"_darcs",
			"build",
			"CVS",
			"dist",
			"node_modules",
			"venv",
			"{arch}",
		],
	)
	parser.addini(
		"testpaths",
		"Directories to search for tests when no files or directories are given on the "
		"command line",
		type="args",
		default=[],
	)
	group = parser.getgroup("general", "Running and selection options")
	group._addoption(
		"-x",
		"--exitfirst",
		action="store_const",
		dest="maxfail",
		const=1,
		help="Exit instantly on first error or failed test",
	)
	group = parser.getgroup("pytest-warnings")
	group.addoption(
		"-W",
		"--pythonwarnings",
		action="append",
		help="Set which warnings to report, see -W option of Python itself",
	)
	parser.addini(
		"filterwarnings",
		type="linelist",
		help="Each line specifies a pattern for "
		"warnings.filterwarnings. "
		"Processed after -W/--pythonwarnings.",
	)
	group._addoption(
		"--maxfail",
		metavar="num",
		action="store",
		type=int,
		dest="maxfail",
		default=0,
		help="Exit after first num failures or errors",
	)
	group._addoption(
		"--strict-config",
		action="store_true",
		help="Any warnings encountered while parsing the `pytest` section of the "
		"configuration file raise errors",
	)
	group._addoption(
		"--strict-markers",
		action="store_true",
		help="Markers not registered in the `markers` section of the configuration "
		"file raise errors",
	)
	group._addoption(
		"--strict",
		action="store_true",
		help="(Deprecated) alias to --strict-markers",
	)
	group._addoption(
		"-c",
		"--config-file",
		metavar="FILE",
		type=str,
		dest="inifilename",
		help="Load configuration from `FILE` instead of trying to locate one of the "
		"implicit configuration files.",
	)
	group._addoption(
		"--continue-on-collection-errors",
		action="store_true",
		default=False,
		dest="continue_on_collection_errors",
		help="Force test execution even if collection errors occur",
	)
	group._addoption(
		"--rootdir",
		action="store",
		dest="rootdir",
		help="Define root directory for tests. Can be relative path: 'root_dir', './root_dir', "
		"'root_dir/another_dir/'; absolute path: '/home/user/root_dir'; path with variables: "
		"'$HOME/root_dir'.",
	)

	group = parser.getgroup("collect", "collection")
	group.addoption(
		"--collectonly",
		"--collect-only",
		"--co",
		action="store_true",
		help="Only collect tests, don't execute them",
	)
	group.addoption(
		"--pyargs",
		action="store_true",
		help="Try to interpret all arguments as Python packages",
	)
	group.addoption(
		"--ignore",
		action="append",
		metavar="path",
		help="Ignore path during collection (multi-allowed)",
	)
	group.addoption(
		"--ignore-glob",
		action="append",
		metavar="path",
		help="Ignore path pattern during collection (multi-allowed)",
	)
	group.addoption(
		"--deselect",
		action="append",
		metavar="nodeid_prefix",
		help="Deselect item (via node id prefix) during collection (multi-allowed)",
	)
	group.addoption(
		"--confcutdir",
		dest="confcutdir",
		default=None,
		metavar="dir",
		type=functools.partial(directory_arg, optname="--confcutdir"),
		help="Only load conftest.py's relative to specified dir",
	)
	group.addoption(
		"--noconftest",
		action="store_true",
		dest="noconftest",
		default=False,
		help="Don't load any conftest.py files",
	)
	group.addoption(
		"--keepduplicates",
		"--keep-duplicates",
		action="store_true",
		dest="keepduplicates",
		default=False,
		help="Keep duplicate tests",
	)
	group.addoption(
		"--collect-in-virtualenv",
		action="store_true",
		dest="collect_in_virtualenv",
		default=False,
		help="Don't ignore tests in a local virtualenv directory",
	)
	group.addoption(
		"--import-mode",
		default="prepend",
		choices=["prepend", "append", "importlib"],
		dest="importmode",
		help="Prepend/append to sys.path when importing test modules and conftest "
		"files. Default: prepend.",
	)

	group = parser.getgroup("debugconfig", "test session debugging and configuration")
	group.addoption(
		"--basetemp",
		dest="basetemp",
		default=None,
		type=validate_basetemp,
		metavar="dir",
		help=(
			"Base temporary directory for this test run. "
			"(Warning: this directory is removed if it exists.)"
		),
	)


def validate_basetemp(path: str) -> str:
	# GH 7119
	msg = "basetemp must not be empty, the current working directory or any parent directory of it"

	# empty path
	if not path:
		raise argparse.ArgumentTypeError(msg)

	def is_ancestor(base: Path, query: Path) -> bool:
		"""Return whether query is an ancestor of base."""
		if base == query:
			return True
		return query in base.parents

	# check if path is an ancestor of cwd
	if is_ancestor(Path.cwd(), Path(path).absolute()):
		raise argparse.ArgumentTypeError(msg)

	# check symlinks for ancestors
	if is_ancestor(Path.cwd().resolve(), Path(path).resolve()):
		raise argparse.ArgumentTypeError(msg)

	return path


def wrap_session(
	config: Config, doit: Callable[[Config, "Session"], int | ExitCode | None]
) -> int | ExitCode:
	"""Skeleton command line program."""
	session = Session.from_config(config)
	session.exitstatus = ExitCode.OK
	initstate = 0
	try:
		try:
			config._do_configure()
			initstate = 1
			config.hook.pytest_sessionstart(session=session)
			initstate = 2
			session.exitstatus = doit(config, session) or 0
		except UsageError:
			session.exitstatus = ExitCode.USAGE_ERROR
			raise
		except Failed:
			session.exitstatus = ExitCode.TESTS_FAILED
		except (KeyboardInterrupt, exit.Exception):
			excinfo = _pytest._code.ExceptionInfo.from_current()
			exitstatus: int | ExitCode = ExitCode.INTERRUPTED
			if isinstance(excinfo.value, exit.Exception):
				if excinfo.value.returncode is not None:
					exitstatus = excinfo.value.returncode
				if initstate < 2:
					sys.stderr.write(f"{excinfo.typename}: {excinfo.value.msg}\n")
			config.hook.pytest_keyboard_interrupt(excinfo=excinfo)
			session.exitstatus = exitstatus
		except BaseException:
			session.exitstatus = ExitCode.INTERNAL_ERROR
			excinfo = _pytest._code.ExceptionInfo.from_current()
			try:
				config.notify_exception(excinfo, config.option)
			except exit.Exception as exc:
				if exc.returncode is not None:
					session.exitstatus = exc.returncode
				sys.stderr.write(f"{type(exc).__name__}: {exc}\n")
			else:
				if isinstance(excinfo.value, SystemExit):
					sys.stderr.write("mainloop: caught unexpected SystemExit!\n")

	finally:
		# Explicitly break reference cycle.
		excinfo = None  # type: ignore
		os.chdir(session.startpath)
		if initstate >= 2:
			try:
				config.hook.pytest_sessionfinish(
					session=session, exitstatus=session.exitstatus
				)
			except exit.Exception as exc:
				if exc.returncode is not None:
					session.exitstatus = exc.returncode
				sys.stderr.write(f"{type(exc).__name__}: {exc}\n")
		config._ensure_unconfigure()
	return session.exitstatus


def pytest_cmdline_main(config: Config) -> int | ExitCode:
	return wrap_session(config, _main)


def _main(config: Config, session: "Session") -> int | ExitCode | None:
	"""Default command line protocol for initialization, session,
	running tests and reporting."""
	config.hook.pytest_collection(session=session)
	config.hook.pytest_runtestloop(session=session)

	if session.testsfailed:
		return ExitCode.TESTS_FAILED
	elif session.testscollected == 0:
		return ExitCode.NO_TESTS_COLLECTED
	return None


def pytest_collection(session: "Session") -> None:
	session.perform_collect()


def pytest_runtestloop(session: "Session") -> bool:
	if session.testsfailed and not session.config.option.continue_on_collection_errors:
		raise session.Interrupted(
			"%d error%s during collection"
			% (session.testsfailed, "s" if session.testsfailed != 1 else "")
		)

	if session.config.option.collectonly:
		return True

	for i, item in enumerate(session.items):
		nextitem = session.items[i + 1] if i + 1 < len(session.items) else None
		item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem)
		if session.shouldfail:
			raise session.Failed(session.shouldfail)
		if session.shouldstop:
			raise session.Interrupted(session.shouldstop)
	return True


def _in_venv(path: Path) -> bool:
	"""Attempt to detect if ``path`` is the root of a Virtual Environment by
	checking for the existence of the appropriate activate script."""
	bindir = path.joinpath("Scripts" if sys.platform.startswith("win") else "bin")
	try:
		if not bindir.is_dir():
			return False
	except OSError:
		return False
	activates = (
		"activate",
		"activate.csh",
		"activate.fish",
		"Activate",
		"Activate.bat",
		"Activate.ps1",
	)
	return any(fname.name in activates for fname in bindir.iterdir())


def pytest_ignore_collect(collection_path: Path, config: Config) -> bool | None:
	ignore_paths = config._getconftest_pathlist(
		"collect_ignore", path=collection_path.parent, rootpath=config.rootpath
	)
	ignore_paths = ignore_paths or []
	excludeopt = config.getoption("ignore")
	if excludeopt:
		ignore_paths.extend(absolutepath(x) for x in excludeopt)

	if collection_path in ignore_paths:
		return True

	ignore_globs = config._getconftest_pathlist(
		"collect_ignore_glob", path=collection_path.parent, rootpath=config.rootpath
	)
	ignore_globs = ignore_globs or []
	excludeglobopt = config.getoption("ignore_glob")
	if excludeglobopt:
		ignore_globs.extend(absolutepath(x) for x in excludeglobopt)

	if any(fnmatch.fnmatch(str(collection_path), str(glob)) for glob in ignore_globs):
		return True

	allow_in_venv = config.getoption("collect_in_virtualenv")
	if not allow_in_venv and _in_venv(collection_path):
		return True

	if collection_path.is_dir():
		norecursepatterns = config.getini("norecursedirs")
		if any(fnmatch_ex(pat, collection_path) for pat in norecursepatterns):
			return True

	return None


def pytest_collection_modifyitems(items: list[nodes.Item], config: Config) -> None:
	deselect_prefixes = tuple(config.getoption("deselect") or [])
	if not deselect_prefixes:
		return

	remaining = []
	deselected = []
	for colitem in items:
		if colitem.nodeid.startswith(deselect_prefixes):
			deselected.append(colitem)
		else:
			remaining.append(colitem)

	if deselected:
		config.hook.pytest_deselected(items=deselected)
		items[:] = remaining


class FSHookProxy:
	def __init__(self, pm: PytestPluginManager, remove_mods) -> None:
		self.pm = pm
		self.remove_mods = remove_mods

	def __getattr__(self, name: str):
		x = self.pm.subset_hook_caller(name, remove_plugins=self.remove_mods)
		self.__dict__[name] = x
		return x


class Interrupted(KeyboardInterrupt):
	"""Signals that the test run was interrupted."""

	__module__ = "builtins"  # For py3.


class Failed(Exception):
	"""Signals a stop as failed test run."""


@dataclasses.dataclass
class _bestrelpath_cache(dict[Path, str]):
	__slots__ = ("path",)

	path: Path

	def __missing__(self, path: Path) -> str:
		r = bestrelpath(self.path, path)
		self[path] = r
		return r


@final
class Session(nodes.FSCollector):
	"""The root of the collection tree.

	``Session`` collects the initial paths given as arguments to pytest.
	"""

	Interrupted = Interrupted
	Failed = Failed
	# Set on the session by runner.pytest_sessionstart.
	_setupstate: SetupState
	# Set on the session by fixtures.pytest_sessionstart.
	_fixturemanager: FixtureManager
	exitstatus: int | ExitCode

	def __init__(self, config: Config) -> None:
		super().__init__(
			path=config.rootpath,
			fspath=None,
			parent=None,
			config=config,
			session=self,
			nodeid="",
		)
		self.testsfailed = 0
		self.testscollected = 0
		self.shouldstop: bool | str = False
		self.shouldfail: bool | str = False
		self.trace = config.trace.root.get("collection")
		self._initialpaths: frozenset[Path] = frozenset()

		self._bestrelpathcache: dict[Path, str] = _bestrelpath_cache(config.rootpath)

		self.config.pluginmanager.register(self, name="session")

	@classmethod
	def from_config(cls, config: Config) -> "Session":
		session: Session = cls._create(config=config)
		return session

	def __repr__(self) -> str:
		return "<%s %s exitstatus=%r testsfailed=%d testscollected=%d>" % (
			self.__class__.__name__,
			self.name,
			getattr(self, "exitstatus", "<UNSET>"),
			self.testsfailed,
			self.testscollected,
		)

	@property
	def startpath(self) -> Path:
		"""The path from which pytest was invoked.

		.. versionadded:: 7.0.0
		"""
		return self.config.invocation_params.dir

	def _node_location_to_relpath(self, node_path: Path) -> str:
		# bestrelpath is a quite slow function.
		return self._bestrelpathcache[node_path]

	@hookimpl(tryfirst=True)
	def pytest_collectstart(self) -> None:
		if self.shouldfail:
			raise self.Failed(self.shouldfail)
		if self.shouldstop:
			raise self.Interrupted(self.shouldstop)

	@hookimpl(tryfirst=True)
	def pytest_runtest_logreport(self, report: TestReport | CollectReport) -> None:
		if report.failed and not hasattr(report, "wasxfail"):
			self.testsfailed += 1
			maxfail = self.config.getvalue("maxfail")
			if maxfail and self.testsfailed >= maxfail:
				self.shouldfail = "stopping after %d failures" % (self.testsfailed)

	pytest_collectreport = pytest_runtest_logreport

	def isinitpath(self, path: Union[str, "os.PathLike[str]"]) -> bool:
		# Optimization: Path(Path(...)) is much slower than isinstance.
		path_ = path if isinstance(path, Path) else Path(path)
		return path_ in self._initialpaths

	def gethookproxy(self, fspath: "os.PathLike[str]"):
		# Optimization: Path(Path(...)) is much slower than isinstance.
		path = fspath if isinstance(fspath, Path) else Path(fspath)
		pm = self.config.pluginmanager
		# Check if we have the common case of running
		# hooks with all conftest.py files.
		my_conftestmodules = pm._getconftestmodules(
			path,
			self.config.getoption("importmode"),
			rootpath=self.config.rootpath,
		)
		remove_mods = pm._conftest_plugins.difference(my_conftestmodules)
		if remove_mods:
			# One or more conftests are not in use at this fspath.
			from .config.compat import PathAwareHookProxy

			proxy = PathAwareHookProxy(FSHookProxy(pm, remove_mods))
		else:
			# All plugins are active for this fspath.
			proxy = self.config.hook
		return proxy

	def _recurse(self, direntry: "os.DirEntry[str]") -> bool:
		if direntry.name == "__pycache__":
			return False
		fspath = Path(direntry.path)
		ihook = self.gethookproxy(fspath.parent)
		if ihook.pytest_ignore_collect(collection_path=fspath, config=self.config):
			return False
		return True

	def _collectfile(
		self, fspath: Path, handle_dupes: bool = True
	) -> Sequence[nodes.Collector]:
		assert fspath.is_file(), f"{fspath!r} is not a file (isdir={fspath.is_dir()!r}, exists={fspath.exists()!r}, islink={fspath.is_symlink()!r})"
		ihook = self.gethookproxy(fspath)
		if not self.isinitpath(fspath):
			if ihook.pytest_ignore_collect(collection_path=fspath, config=self.config):
				return ()

		if handle_dupes:
			keepduplicates = self.config.getoption("keepduplicates")
			if not keepduplicates:
				duplicate_paths = self.config.pluginmanager._duplicatepaths
				if fspath in duplicate_paths:
					return ()
				else:
					duplicate_paths.add(fspath)

		return ihook.pytest_collect_file(file_path=fspath, parent=self)  # type: ignore[no-any-return]

	@overload
	def perform_collect(
		self, args: Sequence[str] | None = ..., genitems: "Literal[True]" = ...
	) -> Sequence[nodes.Item]: ...

	@overload
	def perform_collect(  # noqa: F811
		self, args: Sequence[str] | None = ..., genitems: bool = ...
	) -> Sequence[nodes.Item | nodes.Collector]: ...

	def perform_collect(  # noqa: F811
		self, args: Sequence[str] | None = None, genitems: bool = True
	) -> Sequence[nodes.Item | nodes.Collector]:
		"""Perform the collection phase for this session.

		This is called by the default :hook:`pytest_collection` hook
		implementation; see the documentation of this hook for more details.
		For testing purposes, it may also be called directly on a fresh
		``Session``.

		This function normally recursively expands any collectors collected
		from the session to their items, and only items are returned. For
		testing purposes, this may be suppressed by passing ``genitems=False``,
		in which case the return value contains these collectors unexpanded,
		and ``session.items`` is empty.
		"""
		if args is None:
			args = self.config.args

		self.trace("perform_collect", self, args)
		self.trace.root.indent += 1

		self._notfound: list[tuple[str, Sequence[nodes.Collector]]] = []
		self._initial_parts: list[tuple[Path, list[str]]] = []
		self.items: list[nodes.Item] = []

		hook = self.config.hook

		items: Sequence[nodes.Item | nodes.Collector] = self.items
		try:
			initialpaths: list[Path] = []
			for arg in args:
				fspath, parts = resolve_collection_argument(
					self.config.invocation_params.dir,
					arg,
					as_pypath=self.config.option.pyargs,
				)
				self._initial_parts.append((fspath, parts))
				initialpaths.append(fspath)
			self._initialpaths = frozenset(initialpaths)
			rep = collect_one_node(self)
			self.ihook.pytest_collectreport(report=rep)
			self.trace.root.indent -= 1
			if self._notfound:
				errors = []
				for arg, collectors in self._notfound:
					if collectors:
						errors.append(
							f"not found: {arg}\n(no name {arg!r} in any of {collectors!r})"
						)
					else:
						errors.append(f"found no collectors for {arg}")

				raise UsageError(*errors)
			if not genitems:
				items = rep.result
			else:
				if rep.passed:
					for node in rep.result:
						self.items.extend(self.genitems(node))

			self.config.pluginmanager.check_pending()
			hook.pytest_collection_modifyitems(
				session=self, config=self.config, items=items
			)
		finally:
			hook.pytest_collection_finish(session=self)

		self.testscollected = len(items)
		return items

	def collect(self) -> Iterator[nodes.Item | nodes.Collector]:
		from _pytest.python import Package

		# Keep track of any collected nodes in here, so we don't duplicate fixtures.
		node_cache1: dict[Path, Sequence[nodes.Collector]] = {}
		node_cache2: dict[tuple[type[nodes.Collector], Path], nodes.Collector] = {}

		# Keep track of any collected collectors in matchnodes paths, so they
		# are not collected more than once.
		matchnodes_cache: dict[tuple[type[nodes.Collector], str], CollectReport] = {}

		# Directories of pkgs with dunder-init files.
		pkg_roots: dict[Path, Package] = {}

		for argpath, names in self._initial_parts:
			self.trace("processing argument", (argpath, names))
			self.trace.root.indent += 1

			# Start with a Session root, and delve to argpath item (dir or file)
			# and stack all Packages found on the way.
			# No point in finding packages when collecting doctests.
			if not self.config.getoption("doctestmodules", False):
				pm = self.config.pluginmanager
				for parent in (argpath, *argpath.parents):
					if not pm._is_in_confcutdir(argpath):
						break

					if parent.is_dir():
						pkginit = parent / "__init__.py"
						if pkginit.is_file() and pkginit not in node_cache1:
							col = self._collectfile(pkginit, handle_dupes=False)
							if col:
								if isinstance(col[0], Package):
									pkg_roots[parent] = col[0]
								node_cache1[col[0].path] = [col[0]]

			# If it's a directory argument, recurse and look for any Subpackages.
			# Let the Package collector deal with subnodes, don't collect here.
			if argpath.is_dir():
				assert not names, f"invalid arg {(argpath, names)!r}"

				seen_dirs: set[Path] = set()
				for direntry in visit(argpath, self._recurse):
					if not direntry.is_file():
						continue

					path = Path(direntry.path)
					dirpath = path.parent

					if dirpath not in seen_dirs:
						# Collect packages first.
						seen_dirs.add(dirpath)
						pkginit = dirpath / "__init__.py"
						if pkginit.exists():
							for x in self._collectfile(pkginit):
								yield x
								if isinstance(x, Package):
									pkg_roots[dirpath] = x
					if dirpath in pkg_roots:
						# Do not collect packages here.
						continue

					for x in self._collectfile(path):
						key2 = (type(x), x.path)
						if key2 in node_cache2:
							yield node_cache2[key2]
						else:
							node_cache2[key2] = x
							yield x
			else:
				assert argpath.is_file()

				if argpath in node_cache1:
					col = node_cache1[argpath]
				else:
					collect_root = pkg_roots.get(argpath.parent, self)
					col = collect_root._collectfile(argpath, handle_dupes=False)
					if col:
						node_cache1[argpath] = col

				matching = []
				work: list[
					tuple[Sequence[nodes.Item | nodes.Collector], Sequence[str]]
				] = [(col, names)]
				while work:
					self.trace("matchnodes", col, names)
					self.trace.root.indent += 1

					matchnodes, matchnames = work.pop()
					for node in matchnodes:
						if not matchnames:
							matching.append(node)
							continue
						if not isinstance(node, nodes.Collector):
							continue
						key = (type(node), node.nodeid)
						if key in matchnodes_cache:
							rep = matchnodes_cache[key]
						else:
							rep = collect_one_node(node)
							matchnodes_cache[key] = rep
						if rep.passed:
							submatchnodes = []
							for r in rep.result:
								# TODO: Remove parametrized workaround once collection structure contains
								# parametrization.
								if (
									r.name == matchnames[0]
									or r.name.split("[")[0] == matchnames[0]
								):
									submatchnodes.append(r)
							if submatchnodes:
								work.append((submatchnodes, matchnames[1:]))
						else:
							# Report collection failures here to avoid failing to run some test
							# specified in the command line because the module could not be
							# imported (#134).
							node.ihook.pytest_collectreport(report=rep)

					self.trace("matchnodes finished -> ", len(matching), "nodes")
					self.trace.root.indent -= 1

				if not matching:
					report_arg = "::".join((str(argpath), *names))
					self._notfound.append((report_arg, col))
					continue

				# If __init__.py was the only file requested, then the matched
				# node will be the corresponding Package (by default), and the
				# first yielded item will be the __init__ Module itself, so
				# just use that. If this special case isn't taken, then all the
				# files in the package will be yielded.
				if argpath.name == "__init__.py" and isinstance(matching[0], Package):
					try:
						yield next(iter(matching[0].collect()))
					except StopIteration:
						# The package collects nothing with only an __init__.py
						# file in it, which gets ignored by the default
						# "python_files" option.
						pass
					continue

				yield from matching

			self.trace.root.indent -= 1

	def genitems(self, node: nodes.Item | nodes.Collector) -> Iterator[nodes.Item]:
		self.trace("genitems", node)
		if isinstance(node, nodes.Item):
			node.ihook.pytest_itemcollected(item=node)
			yield node
		else:
			assert isinstance(node, nodes.Collector)
			rep = collect_one_node(node)
			if rep.passed:
				for subnode in rep.result:
					yield from self.genitems(subnode)
			node.ihook.pytest_collectreport(report=rep)


def search_pypath(module_name: str) -> str:
	"""Search sys.path for the given a dotted module name, and return its file system path."""
	try:
		spec = importlib.util.find_spec(module_name)
	# AttributeError: looks like package module, but actually filename
	# ImportError: module does not exist
	# ValueError: not a module name
	except (AttributeError, ImportError, ValueError):
		return module_name
	if spec is None or spec.origin is None or spec.origin == "namespace":
		return module_name
	elif spec.submodule_search_locations:
		return os.path.dirname(spec.origin)
	else:
		return spec.origin


def resolve_collection_argument(
	invocation_path: Path, arg: str, *, as_pypath: bool = False
) -> tuple[Path, list[str]]:
	"""Parse path arguments optionally containing selection parts and return (fspath, names).

	Command-line arguments can point to files and/or directories, and optionally contain
	parts for specific tests selection, for example:

	    "pkg/tests/test_foo.py::TestClass::test_foo"

	This function ensures the path exists, and returns a tuple:

	    (Path("/full/path/to/pkg/tests/test_foo.py"), ["TestClass", "test_foo"])

	When as_pypath is True, expects that the command-line argument actually contains
	module paths instead of file-system paths:

	    "pkg.tests.test_foo::TestClass::test_foo"

	In which case we search sys.path for a matching module, and then return the *path* to the
	found module.

	If the path doesn't exist, raise UsageError.
	If the path is a directory and selection parts are present, raise UsageError.
	"""
	base, squacket, rest = str(arg).partition("[")
	strpath, *parts = base.split("::")
	if parts:
		parts[-1] = f"{parts[-1]}{squacket}{rest}"
	if as_pypath:
		strpath = search_pypath(strpath)
	fspath = invocation_path / strpath
	fspath = absolutepath(fspath)
	if not safe_exists(fspath):
		msg = (
			"module or package not found: {arg} (missing __init__.py?)"
			if as_pypath
			else "file or directory not found: {arg}"
		)
		raise UsageError(msg.format(arg=arg))
	if parts and fspath.is_dir():
		msg = (
			"package argument cannot contain :: selection parts: {arg}"
			if as_pypath
			else "directory argument cannot contain :: selection parts: {arg}"
		)
		raise UsageError(msg.format(arg=arg))
	return fspath, parts
