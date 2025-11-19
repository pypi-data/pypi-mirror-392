"""
Purposely: Purpose-Driven Development Framework

A CLI tool for maintaining project purpose throughout development lifecycle.
"""

try:
    from importlib.metadata import version
    __version__ = version("purposely")
except Exception:
    # Fallback for development (before pip install -e .)
    __version__ = "0.0.0-dev"

__author__ = "Purposely Team"
__license__ = "MIT"

from .cli import cli

__all__ = ["cli"]
