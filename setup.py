from setuptools import find_packages, setup
from demo_cicd_ide_multiws import __version__

setup(
    name="demo_cicd_ide_multiws",
    packages=find_packages(exclude=["tests", "tests.*"]),
    setup_requires=["wheel"],
    version=__version__,
    description="",
    author=""
)
