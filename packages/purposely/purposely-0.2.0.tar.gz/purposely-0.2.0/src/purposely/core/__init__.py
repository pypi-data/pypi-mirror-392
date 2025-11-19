"""
Core functionality for Purposely.

This package contains the core logic for:
- Project initialization (initializer.py)
- Template rendering (renderer.py)
"""

from .initializer import Initializer
from .renderer import TemplateRenderer

__all__ = ["Initializer", "TemplateRenderer"]
