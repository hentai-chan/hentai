#!/usr/bin/env python
import re

from setuptools import setup

with open("hentai/__init__.py", encoding='utf8') as file_handler:
    version = re.search(r'__version__ = "(.*?)"', file_handler.read()).group(1)

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="hentai",
    version=version,
    install_requires=["requests"],
)
