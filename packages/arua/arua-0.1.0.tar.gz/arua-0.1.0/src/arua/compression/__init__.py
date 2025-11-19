"""Compression utilities for the ARUA package."""

from __future__ import annotations

from .core import compress, decompress
from .lz77 import compress as lz77_compress
from .lz77 import decompress as lz77_decompress

__all__ = ["compress", "decompress", "lz77_compress", "lz77_decompress"]
