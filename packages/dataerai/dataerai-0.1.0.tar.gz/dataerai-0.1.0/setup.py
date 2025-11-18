import setuptools
from os import path
import os

# read the contents of README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README"), encoding="utf-8") as f:
    long_description = f.read()


with open("requirements.txt", "r") as f:
    install_requires = [line.strip() for line in f]

# Load version without importing the package (avoids import side-effects during build)
version_ns = {}
version_file = path.join(this_directory, "dataerai", "VERSION.py")
with open(version_file, "r") as vf:
    exec(vf.read(), version_ns)
__version__ = version_ns.get("__version__", "0.0.0")

setuptools.setup(
    name=os.getenv("DATAERAI_PYPI_REPO", "dataerai"),
    version=__version__,
    author="Dataerai, LLC",
    author_email="info@dataerai.com",
    description="Portal CLI and API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dataerai/datafed",
    packages=setuptools.find_packages(),
    setup_requires=["setuptools"],
    install_requires=install_requires,
    entry_points={"console_scripts": ["dataerai = dataerai.CLI:run"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
