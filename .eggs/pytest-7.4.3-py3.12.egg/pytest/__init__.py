# PYTHON_ARGCOMPLETE_OK
"""pytest: unit and functional testing with Python."""

from _pytest import __version__, version_tuple
from _pytest._code import ExceptionInfo
from _pytest.assertion import register_assert_rewrite
from _pytest.cacheprovider import Cache
from _pytest.capture import CaptureFixture
from _pytest.config import (
	Config,
	ExitCode,
	PytestPluginManager,
	UsageError,
	cmdline,
	console_main,
	hookimpl,
	hookspec,
	main,
)
from _pytest.config.argparsing import OptionGroup, Parser
from _pytest.debugging import pytestPDB as __pytestPDB
from _pytest.doctest import DoctestItem
from _pytest.fixtures import FixtureLookupError, FixtureRequest, fixture, yield_fixture
from _pytest.freeze_support import freeze_includes
from _pytest.legacypath import TempdirFactory, Testdir
from _pytest.logging import LogCaptureFixture
from _pytest.main import Session
from _pytest.mark import MARK_GEN as mark
from _pytest.mark import Mark, MarkDecorator, MarkGenerator, param
from _pytest.monkeypatch import MonkeyPatch
from _pytest.nodes import Collector, File, Item
from _pytest.outcomes import exit, fail, importorskip, skip, xfail
from _pytest.pytester import (
	HookRecorder,
	LineMatcher,
	Pytester,
	RecordedHookCall,
	RunResult,
)
from _pytest.python import Class, Function, Metafunc, Module, Package
from _pytest.python_api import approx, raises
from _pytest.recwarn import WarningsRecorder, deprecated_call, warns
from _pytest.reports import CollectReport, TestReport
from _pytest.runner import CallInfo
from _pytest.stash import Stash, StashKey
from _pytest.terminal import TestShortLogReport
from _pytest.tmpdir import TempPathFactory
from _pytest.warning_types import (
	PytestAssertRewriteWarning,
	PytestCacheWarning,
	PytestCollectionWarning,
	PytestConfigWarning,
	PytestDeprecationWarning,
	PytestExperimentalApiWarning,
	PytestRemovedIn8Warning,
	PytestReturnNotNoneWarning,
	PytestUnhandledCoroutineWarning,
	PytestUnhandledThreadExceptionWarning,
	PytestUnknownMarkWarning,
	PytestUnraisableExceptionWarning,
	PytestWarning,
)

set_trace = __pytestPDB.set_trace


__all__ = [
	"__version__",
	"approx",
	"Cache",
	"CallInfo",
	"CaptureFixture",
	"Class",
	"cmdline",
	"Collector",
	"CollectReport",
	"Config",
	"console_main",
	"deprecated_call",
	"DoctestItem",
	"exit",
	"ExceptionInfo",
	"ExitCode",
	"fail",
	"File",
	"fixture",
	"FixtureLookupError",
	"FixtureRequest",
	"freeze_includes",
	"Function",
	"hookimpl",
	"HookRecorder",
	"hookspec",
	"importorskip",
	"Item",
	"LineMatcher",
	"LogCaptureFixture",
	"main",
	"mark",
	"Mark",
	"MarkDecorator",
	"MarkGenerator",
	"Metafunc",
	"Module",
	"MonkeyPatch",
	"OptionGroup",
	"Package",
	"param",
	"Parser",
	"PytestAssertRewriteWarning",
	"PytestCacheWarning",
	"PytestCollectionWarning",
	"PytestConfigWarning",
	"PytestDeprecationWarning",
	"PytestExperimentalApiWarning",
	"PytestRemovedIn8Warning",
	"PytestReturnNotNoneWarning",
	"Pytester",
	"PytestPluginManager",
	"PytestUnhandledCoroutineWarning",
	"PytestUnhandledThreadExceptionWarning",
	"PytestUnknownMarkWarning",
	"PytestUnraisableExceptionWarning",
	"PytestWarning",
	"raises",
	"RecordedHookCall",
	"register_assert_rewrite",
	"RunResult",
	"Session",
	"set_trace",
	"skip",
	"Stash",
	"StashKey",
	"version_tuple",
	"TempdirFactory",
	"TempPathFactory",
	"Testdir",
	"TestReport",
	"TestShortLogReport",
	"UsageError",
	"WarningsRecorder",
	"warns",
	"xfail",
	"yield_fixture",
]


def __getattr__(name: str) -> object:
	if name == "Instance":
		# The import emits a deprecation warning.
		from _pytest.python import Instance

		return Instance
	raise AttributeError(f"module {__name__} has no attribute {name}")
