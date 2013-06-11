import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "py_qt_propgrid",
    version = "0.0.1",
    author = "Sam Price",
    author_email = "TheSamPrice@gmail.com",
    description = ("Tools to make property grids easier to work with."), 
    license = "LGPL",
    keywords = "QT Property Grid",
    url = "http://packages.python.org/py_qt_propgrid",
    packages=['py_qt_propgrid'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
