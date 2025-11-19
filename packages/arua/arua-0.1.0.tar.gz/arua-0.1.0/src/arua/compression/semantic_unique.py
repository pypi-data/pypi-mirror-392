"""Semantic Unique (Su) codec (CPU placeholder).

This module implements a minimal, in-process content-addressable store
for deduplicating repeated payloads. It is intended as a prototype for
Su behaviour and is wired into the semantic codec pipeline.

Body format:

    0x00 [16B fp][4B len][len bytes core_payload]   # literal + store
    0x01 [16B fp]                                   # reference

Where:
    * ``fp`` is a 16-byte truncated SHA-256 fingerprint of the *raw*
      payload bytes before compression.
    * ``core_payload`` is produced by :mod:`arua.compression.core`.
"""

from __future__ import annotations

import hashlib
import threading
from typing import Dict

from .core import compress as core_compress
from .core import decompress as core_decompress
from .semantic_store import ShardedStore, SemanticStore

_FP_SIZE = 16
_TAG_LITERAL = 0x00
_TAG_REF = 0x01
_MAX_STORED_CORE_PAYLOAD = 1_048_576  # 1 MiB cap for store entries


class MissingUniqueChunkError(RuntimeError):
    """Raised when a referenced Su fingerprint is not present in the store."""


_STORE: SemanticStore = ShardedStore()
_STORE_LOCK = threading.Lock()


def _fingerprint(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()[:_FP_SIZE]


def compress(data: bytes) -> bytes:
    """Compress data using a simple Su content-addressed scheme."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")
    raw = bytes(data)
    fp = _fingerprint(raw)
    with _STORE_LOCK:
        existing = _STORE.get(fp)
    if existing is not None:
        out = bytearray()
        out.append(_TAG_REF)
        out.extend(fp)
        return bytes(out)

    core_payload = core_compress(raw, method="auto")
    # Only store reasonably-sized payloads to keep the dedup store bounded.
    if len(core_payload) <= _MAX_STORED_CORE_PAYLOAD:
        with _STORE_LOCK:
            _STORE.put(fp, core_payload)

    out = bytearray()
    out.append(_TAG_LITERAL)
    out.extend(fp)
    out.extend(len(core_payload).to_bytes(4, "big"))
    out.extend(core_payload)
    return bytes(out)


def decompress(payload: bytes) -> bytes:
    """Decompress data produced by :func:`compress`."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")
    data = memoryview(payload)
    if len(data) < 1 + _FP_SIZE:
        raise ValueError("Su payload too short")
    tag = data[0]
    offset = 1
    fp = bytes(data[offset : offset + _FP_SIZE])
    offset += _FP_SIZE

    if tag == _TAG_LITERAL:
        if offset + 4 > len(data):
            raise ValueError("Su literal missing length")
        length = int.from_bytes(data[offset : offset + 4], "big")
        offset += 4
        if offset + length > len(data):
            raise ValueError("Su literal length out of range")
        core_payload = bytes(data[offset : offset + length])
        with _STORE_LOCK:
            _STORE.put(fp, core_payload)
        return core_decompress(core_payload)

    if tag == _TAG_REF:
        with _STORE_LOCK:
            core_payload = _STORE.get(fp)
        if core_payload is None:
            raise MissingUniqueChunkError("missing Su chunk for fingerprint")
        return core_decompress(core_payload)

    raise ValueError(f"unknown Su tag: {tag}")


def reset_unique_store() -> None:
    """Reset the Su in-memory store (for tests)."""
    with _STORE_LOCK:
        _STORE.reset()


def get_unique_store_snapshot() -> Dict[bytes, bytes]:
    """Return a shallow copy of the Su store."""
    with _STORE_LOCK:
        return _STORE.snapshot()
