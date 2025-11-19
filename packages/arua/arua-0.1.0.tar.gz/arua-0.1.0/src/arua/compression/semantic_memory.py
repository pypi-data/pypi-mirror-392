"""Semantic Memory (Sm) codec (CPU placeholder).

This module implements a simple multi-chunk wrapper on top of the
Semantic Unique (Su) codec. It is intended to model memory-oriented
compression where large payloads are split into blocks that can be
deduplicated and cached independently.

Body format:

    [n * (4B len | len bytes su_segment)]

Each ``su_segment`` is a full Su payload (literal or ref). The semantic
header for the Sm payload still carries the usual codec/domain/template
fields; this module only defines the Sm *body*.
"""

from __future__ import annotations

import struct
from typing import Iterable

from .semantic_unique import compress as su_compress
from .semantic_unique import decompress as su_decompress

_LEN_STRUCT = struct.Struct(">I")
DEFAULT_BLOCK_SIZE = 64 * 1024


def compress(data: bytes, block_size: int = DEFAULT_BLOCK_SIZE) -> bytes:
    """Compress data using a simple Sm multi-chunk scheme built on Su."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")
    raw = bytes(data)
    out = bytearray()
    i = 0
    while i < len(raw):
        chunk = raw[i : i + block_size]
        su_segment = su_compress(chunk)
        out.extend(_LEN_STRUCT.pack(len(su_segment)))
        out.extend(su_segment)
        i += block_size
    return bytes(out)


def decompress(payload: bytes) -> bytes:
    """Decompress data produced by :func:`compress`."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")
    data = memoryview(payload)
    out = bytearray()
    offset = 0
    while offset < len(data):
        if offset + _LEN_STRUCT.size > len(data):
            raise ValueError("Sm payload truncated before segment length")
        (length,) = _LEN_STRUCT.unpack_from(data, offset)
        offset += _LEN_STRUCT.size
        if offset + length > len(data):
            raise ValueError("Sm segment length out of range")
        segment = bytes(data[offset : offset + length])
        offset += length
        out.extend(su_decompress(segment))
    return bytes(out)

