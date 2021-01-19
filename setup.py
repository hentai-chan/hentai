#!/usr/bin/env python3

import re

from setuptools import setup

with open("hentai/__init__.py", encoding='utf8') as file_handler:
    lines = file_handler.read()
    version = re.search(r'__version__ = "(.*?)"', lines).group(1)
    package_name = re.search(r'package_name = "(.*?)"', lines).group(1)

with open("requirements.txt", encoding='utf-8') as file_handler:
    packages = file_handler.read().splitlines()

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name=package_name,
    version=version,
    install_requires=packages,
    include_package_data=True
)
