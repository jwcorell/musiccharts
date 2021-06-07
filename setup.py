#!/usr/bin/env python3
"""
setup.py

Setup module for musicCharts
"""

import re
from pathlib import Path

from setuptools import setup

try:
    __version__ = re.findall(
        '__version__ = "(.*)"', open("musiccharts/__init__.py").read()
    )[0]
except FileNotFoundError:
    print("Version info not found!\n")
    sys.exit(0)

setup(
    name="musiccharts",
    version=__version__,
    description="Generate music chart PDFs in multiple keys and NNS",
    license="GNU General Public License",
    author="James Corell",
    author_email="github@jamesw.us",
    url="...",
    python_requires=">=3.6",
    install_requires=["PyLaTeX", "setuptools"],
    packages=["musiccharts"],
    package_data={"": ["VERSION"]},
    include_package_data=True,
    entry_points={"console_scripts": ["musiccharts=musiccharts.cli:main"]},
)
