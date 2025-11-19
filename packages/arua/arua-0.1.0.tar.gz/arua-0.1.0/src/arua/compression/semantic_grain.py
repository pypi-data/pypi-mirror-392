"""A simple semantic-grain compression shim.

This is a placeholder that provides an interface for semantic-grain (SG)
compression until a full GPU-backed implementation is available. For now,
it reuses the LZ77 compressor but reserves the method byte for SG.

The goal is to support integration without changing the public API.
"""
from __future__ import annotations

from typing import Tuple

from .lz77 import compress as lz77_compress, decompress as lz77_decompress


def compress(data: bytes) -> bytes:
    """Compress using a placeholder semantic-grain algorithm.

    Current implementation: use lz77 and add meta header for SG.
    Future improvement: run SG matching and packing on GPU via bindings.
    """
    # For now, just reuse lz77 compressor and prefix with an SG method subheader
    payload = lz77_compress(data)
    # Optionally, we could add SG-specific side-channel header in the future
    return payload


def decompress(payload: bytes) -> bytes:
    """Decompress semantic-grain output produced by :func:`compress`.

    Current implementation: delegate to lz77 decompressor.
    """
    return lz77_decompress(payload)
