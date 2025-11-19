"""Core ARUA compressor: method byte + LZ77/uncompressed.

This module provides a small, dependency-free compression API that can be
used without relying on the external AURA project.
"""

from __future__ import annotations

from typing import Literal

from .grain import compress as grain_compress
from .grain import decompress as grain_decompress
from .lz77 import compress as lz77_compress
from .lz77 import decompress as lz77_decompress

MethodName = Literal["auto", "uncompressed", "lz77", "sg"]

METHOD_UNCOMPRESSED = 0x00
METHOD_LZ77 = 0x01
METHOD_SG = 0x02


def compress(data: bytes, method: MethodName = "auto") -> bytes:
    """Compress data using a simple method-byte wrapper.

    Format:
        [method_byte][method_specific_payload]

    Methods:
        * ``uncompressed`` – payload is the original bytes.
        * ``lz77`` – payload is produced by :mod:`arua.compression.lz77`.
        * ``auto`` – try LZ77 and fall back to uncompressed if it expands.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    raw = bytes(data)

    if method == "uncompressed":
        return bytes([METHOD_UNCOMPRESSED]) + raw

    if method == "lz77":
        payload = lz77_compress(raw)
        return bytes([METHOD_LZ77]) + payload

    if method == "sg":
        payload = grain_compress(raw)
        return bytes([METHOD_SG]) + payload

    if method != "auto":
        raise ValueError(f"unsupported method: {method}")

    # auto: try LZ77 and Sg, but do not expand data; prefer Sg when sizes tie.
    candidates: list[bytes] = []

    lz_payload = lz77_compress(raw)
    lz_candidate = bytes([METHOD_LZ77]) + lz_payload
    candidates.append(lz_candidate)

    sg_payload = grain_compress(raw)
    sg_candidate = bytes([METHOD_SG]) + sg_payload
    candidates.append(sg_candidate)

    # Always include uncompressed as a safety option.
    uncompressed_candidate = bytes([METHOD_UNCOMPRESSED]) + raw
    candidates.append(uncompressed_candidate)

    # Choose the smallest candidate; if sizes tie, prefer Sg, then LZ77.
    def _score(payload: bytes) -> tuple[int, int]:
        method = payload[0]
        # Order: Sg (2) is preferred over LZ77 (1), then uncompressed (0).
        preference = {METHOD_SG: 0, METHOD_LZ77: 1, METHOD_UNCOMPRESSED: 2}.get(
            method, 3
        )
        return len(payload), preference

    best = min(candidates, key=_score)
    # Ensure we never expand significantly beyond raw+1; otherwise fall back.
    if len(best) > len(raw) + 1:
        return bytes([METHOD_UNCOMPRESSED]) + raw
    return best


def decompress(payload: bytes) -> bytes:
    """Decompress data produced by :func:`compress`."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")
    if not payload:
        raise ValueError("empty payload")

    method_byte = payload[0]
    body = bytes(payload[1:])

    if method_byte == METHOD_UNCOMPRESSED:
        return body
    if method_byte == METHOD_LZ77:
        return lz77_decompress(body)
    if method_byte == METHOD_SG:
        return grain_decompress(body)

    raise ValueError(f"unknown compression method byte: {method_byte}")
