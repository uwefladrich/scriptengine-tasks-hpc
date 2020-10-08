"""setup.py for package scriptengine-tasks-hpc."""
import os
import codecs
import setuptools

def read(rel_path):
    """
    Helper function to read file in relative path.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()

def get_version(rel_path):
    """
    Helper function to get package version.
    """
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]

setuptools.setup(
    name="scriptengine-tasks-hpc",
    version=get_version("scriptengine/tasks/hpc/version.py"),
    author="Uwe Fladrich",
    author_email="uwe.fladrich@protonmail.com",
    description="ScriptEngine tasks you may need on HPC systems",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/uwefladrich/scriptengine-tasks-hpc",
    packages=[
        "scriptengine.tasks.hpc",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "scriptengine>=0.6",
    ],
)
