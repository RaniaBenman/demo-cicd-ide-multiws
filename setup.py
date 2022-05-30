from setuptools import find_packages, setup
from demo_covea_ide_gitinit import __version__

setup(
    name="demo_covea_ide_gitinit",
    packages=find_packages(exclude=["tests", "tests.*"]),
    setup_requires=["wheel"],
    version=__version__,
    description="",
    author=""
)
