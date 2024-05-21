from setuptools import setup, find_packages


def requirements() -> list[str]:
    with open('requirements.txt', 'r') as file:
        dependencies = file.read().split('\n')
        return [ req for req in dependencies if req != ""]


if __name__ == '__main__':
    print(requirements())
    
    setup(
        name="integration",
        version="0.1.0",
        author="NGCP - Ground Control Station",
        url="https://github.com/Northrop-Grumman-Collaboration-Project/gcs-integration-library",
        packages=find_packages(include=("Commands", "Telemetry", "Types")),
        install_requires=requirements(),
    )
