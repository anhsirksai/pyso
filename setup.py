#! /usr/bin/env python
# Copyright (C) 2010, Jonathon Watney <jonathonwatney@gmail.com>
# See the file LICENSE for licensing terms.

"""
setup.py - installation script for Python distutils
"""

import os
import sys

from distutils import core


_name = "pyso"
_package = "pyso"
_version = open("VERSION").read().strip()


core.setup(
  # Installation data
  name=_name,
  version=_version,
  packages=[_package],
  package_dir={_package: ""},
  data_files=[("doc/pyso", ["README", "LICENSE"])],
  # Metadata
  author="Jonathon Watney",
  author_email="jonathonwatney@gmail.com",
  url="http://github.com/jwatney/pyso",
  description="Python Stack Overflow API bindings.",
  keywords="stack overflow",
  license="Open source (GPL2)",
  platforms=["Pure Python (Python version >= 2.6)"],
  long_description="""\
pyso is an API wrapper for the Stack Overflow API written in Python.
""",
  download_url="http://github.com/jwatney/pyso/tarball/master",
  classifiers=[
    "Development Status :: 4 - Beta",
    "Environment :: Other Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules"
    ]
  )
