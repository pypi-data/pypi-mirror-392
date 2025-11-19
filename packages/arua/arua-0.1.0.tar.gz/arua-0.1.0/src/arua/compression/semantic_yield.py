"""Semantic Yield (Sy) codec.

Sy encodes priority/yield metadata alongside a compressed payload.
The current implementation uses a compact binary header for the core
yield fields plus JSON only for any future, optional extras.

Wire format:

    [2B meta_len][meta_blob][compressed_data]

Where:
    * meta_blob is a UTF-8 JSON object describing yield/priority fields.
    * compressed_data is produced by :mod:`arua.compression.core`.

For hot paths, :func:`encode_yield` and :func:`decode_yield` now use a
fixed binary layout for the primary fields and only fall back to JSON
parsing when necessary to preserve compatibility.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
import struct
from typing import Any, Dict, Optional, Tuple

from .core import compress as core_compress
from .core import decompress as core_decompress


@dataclass(frozen=True)
class YieldMetadata:
    """Yield/priority metadata for a payload."""

    priority: str = "normal"  # e.g. "low", "normal", "high"
    max_latency_ms: Optional[int] = None
    expected_value: Optional[float] = None


_YIELD_STRUCT = struct.Struct(">bhf")


def encode_yield(meta: YieldMetadata) -> bytes:
    """Encode YieldMetadata into a compact binary body.

    Binary layout (big-endian):
        [priority:i8][max_latency_ms:i16][expected_value:f32]

    Where:
        * priority: small signed int bucket (e.g. -1=low,0=normal,1=high).
        * max_latency_ms: clamped to [-32768, 32767] or -1 if None.
        * expected_value: 32-bit float, or 0.0 if None.
    """
    priority_map = {"low": -1, "normal": 0, "high": 1}
    prio_int = priority_map.get(meta.priority, 0)

    if meta.max_latency_ms is None:
        max_latency = -1
    else:
        max_latency = int(meta.max_latency_ms)
        if max_latency < -32768:
            max_latency = -32768
        if max_latency > 32767:
            max_latency = 32767

    expected = 0.0 if meta.expected_value is None else float(meta.expected_value)

    return _YIELD_STRUCT.pack(prio_int, max_latency, expected)


def decode_yield(payload: bytes) -> YieldMetadata:
    """Decode YieldMetadata from a Sy metadata body.

    For v1, this first attempts to parse the compact binary layout used
    by :func:`encode_yield`. If parsing fails (e.g. old JSON blobs),
    it falls back to the legacy JSON format for compatibility.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_yield() expects a bytes-like object")
    data = bytes(payload)
    # Try binary fast-path first.
    if len(data) == _YIELD_STRUCT.size:
        prio_int, max_latency, expected = _YIELD_STRUCT.unpack(data)
        priority_reverse = {-1: "low", 0: "normal", 1: "high"}
        priority = priority_reverse.get(prio_int, "normal")
        max_latency_ms: Optional[int]
        if max_latency < 0:
            max_latency_ms = None
        else:
            max_latency_ms = int(max_latency)
        expected_value: Optional[float]
        # Treat 0.0 as "unset" only if max_latency is also unset; this keeps
        # behaviour simple and avoids losing legitimate zero values in the
        # common case.
        expected_value = float(expected)
        return YieldMetadata(
            priority=priority,
            max_latency_ms=max_latency_ms,
            expected_value=expected_value,
        )

    # Fallback: legacy JSON format.
    try:
        obj = json.loads(data.decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid Sy payload") from exc
    if not isinstance(obj, dict):
        raise ValueError("Sy payload must be a JSON object")
    priority = str(obj.get("priority", "normal"))
    max_latency_ms = obj.get("max_latency_ms")
    expected_value = obj.get("expected_value")
    if max_latency_ms is not None:
        max_latency_ms = int(max_latency_ms)
    if expected_value is not None:
        expected_value = float(expected_value)
    return YieldMetadata(
        priority=priority,
        max_latency_ms=max_latency_ms,
        expected_value=expected_value,
    )


def compress(data: bytes, meta: YieldMetadata | None = None) -> bytes:
    """Compress data with yield/priority metadata."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")
    if meta is None:
        meta = YieldMetadata()

    meta_blob = encode_yield(meta)
    if len(meta_blob) > 0xFFFF:
        raise ValueError("yield metadata too large (max 65535 bytes)")

    compressed_data = core_compress(bytes(data), method="auto")

    meta_len = len(meta_blob)
    length_bytes = bytes([(meta_len >> 8) & 0xFF, meta_len & 0xFF])
    return length_bytes + meta_blob + compressed_data


def decompress(payload: bytes) -> Tuple[bytes, YieldMetadata]:
    """Decompress a Sy payload and extract yield metadata."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    payload = bytes(payload)
    if len(payload) < 2:
        raise ValueError("Sy payload too short (need at least 2 bytes)")

    meta_len = (payload[0] << 8) | payload[1]
    if len(payload) < 2 + meta_len:
        raise ValueError(
            f"Sy payload truncated: expected {2 + meta_len} bytes, got {len(payload)}"
        )

    meta_blob = payload[2 : 2 + meta_len]
    compressed_data = payload[2 + meta_len :]

    meta = decode_yield(meta_blob)
    data = core_decompress(compressed_data)
    return data, meta
