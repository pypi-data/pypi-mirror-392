"""Semantic Z (Sz) codec (CPU placeholder implementation).

This module implements a minimal Sz codec: it breaks the payload into
fixed-size blocks, maintains an in-memory deduplication store keyed by
short fingerprints, and emits either references to existing blocks or
compressed literals.

The implementation is intentionally simple and CPU-only so it can serve
as a prototype for more advanced GPU/CDC-based designs.
"""
from __future__ import annotations

import hashlib
import threading
import zlib
from typing import Dict

from .core import decompress as core_decompress
from .semantic_store import ShardedStore, SemanticStore

# Local in-memory chunk store used for tests / per-process singleton.
_CHUNK_STORE: SemanticStore = ShardedStore()
_CHUNK_STORE_LOCK = threading.Lock()

DEFAULT_BLOCK_SIZE = 64 * 1024
_MAX_STORED_CHUNK = 1_048_576  # 1 MiB cap for Sz chunks


class MissingChunkError(RuntimeError):
    """Raised when a referenced chunk fingerprint is not present."""


def _fingerprint(data: bytes) -> bytes:
    """Return a short fingerprint for a block (truncated SHA-256)."""
    return hashlib.sha256(data).digest()[:8]


def compress(data: bytes, block_size: int = DEFAULT_BLOCK_SIZE) -> bytes:
    """Compress bytes using a simple block-dedup scheme.

    The format is:
        [tag][payload]...

    Where:
        tag = 0x00 => literal block: [4B len][zlib-compressed bytes]
        tag = 0x01 => reference: [8B fingerprint]
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    out = bytearray()
    i = 0
    raw = bytes(data)
    while i < len(raw):
        chunk = raw[i : i + block_size]
        fp = _fingerprint(chunk)
        with _CHUNK_STORE_LOCK:
            cached = _CHUNK_STORE.get(fp) is not None
        if cached:
            out.append(0x01)  # ref
            out.extend(fp)
        else:
            compressed = zlib.compress(chunk, level=9)
            # Only store reasonably-sized chunks to keep the Sz store bounded.
            if len(chunk) <= _MAX_STORED_CHUNK:
                with _CHUNK_STORE_LOCK:
                    _CHUNK_STORE.put(fp, chunk)
            out.append(0x00)  # literal
            out.extend(len(compressed).to_bytes(4, "big"))
            out.extend(compressed)
        i += block_size
    return bytes(out)


def decompress(payload: bytes) -> bytes:
    """Decompress bytes produced by :func:`compress`.

    If the payload does not match the Sz block format, fall back to the
    core decompressor to preserve robustness for legacy data.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    data = memoryview(payload)
    out = bytearray()
    i = 0

    # Best-effort detection: if the stream does not look like Sz, delegate.
    if len(data) and data[0] not in (0x00, 0x01):
        return core_decompress(bytes(payload))

    while i < len(data):
        tag = data[i]
        i += 1
        if tag == 0x01:  # reference
            if i + 8 > len(data):
                raise ValueError("invalid Sz ref token")
            fp = bytes(data[i : i + 8])
            i += 8
            with _CHUNK_STORE_LOCK:
                chunk = _CHUNK_STORE.get(fp)
            if chunk is None:
                raise MissingChunkError("missing referenced Sz chunk fingerprint")
            out.extend(chunk)
        elif tag == 0x00:  # literal
            if i + 4 > len(data):
                raise ValueError("invalid Sz literal header")
            length = int.from_bytes(data[i : i + 4], "big")
            i += 4
            if i + length > len(data):
                raise ValueError("invalid Sz literal length")
            compressed = bytes(data[i : i + length])
            i += length
            out.extend(zlib.decompress(compressed))
        else:
            raise ValueError(f"unknown Sz token type: {tag}")
    return bytes(out)


def reset_chunk_store() -> None:
    """Reset the in-memory chunk store (for tests)."""
    with _CHUNK_STORE_LOCK:
        _CHUNK_STORE.reset()


def get_chunk_store_snapshot() -> Dict[bytes, bytes]:
    """Return a shallow copy of the current chunk store."""
    with _CHUNK_STORE_LOCK:
        return _CHUNK_STORE.snapshot()
