"""Setup script for Manifest.

This file exists for backward compatibility with tools that don't yet
support PEP 517/518 (pyproject.toml-based builds).

For modern installations, use:
    pip install .

For editable development installs:
    pip install -e ".[dev]"
"""

from setuptools import setup

# All configuration is in pyproject.toml
# This file is only needed for backward compatibility
setup()