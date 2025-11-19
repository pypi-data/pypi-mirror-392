"""ARUA package root.

This file exposes the basic package version and re-exports the ASGI app
and calculator helpers for convenience.
"""

from __future__ import annotations

__all__ = ["__version__", "app", "add", "multiply"]
__version__ = "0.1.0"

from .app import app  # re-export for ease of use
from .calculator import add, multiply
