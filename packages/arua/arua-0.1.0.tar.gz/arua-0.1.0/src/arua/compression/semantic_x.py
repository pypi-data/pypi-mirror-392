"""Prototype: Semantic eXperiment (Sx) – local dictionary substitution.

This experimental codec tests whether per-message local dictionaries of
frequent tokens (words) can improve compression for small-to-medium text.
"""

from __future__ import annotations

import re
import zlib
from collections import Counter
from typing import List

from .core import compress as core_compress, decompress as core_decompress

DEFAULT_DICT_SIZE = 64
MIN_TOKEN_LEN = 3

_TOKEN_RE = re.compile(r"(\w+|[^\w]+)")


def _is_text(data: bytes) -> bool:
    try:
        data.decode("utf-8")
        return True
    except Exception:
        return False


def _build_dictionary(text: str, n: int) -> List[str]:
    """Build a local dictionary of frequent word tokens."""
    tokens = re.findall(r"\w+", text)
    if not tokens:
        return []
    freq = Counter(t.lower() for t in tokens if len(t) >= MIN_TOKEN_LEN)
    most = [t for t, _ in freq.most_common(n)]
    return most


def compress_text(data: bytes, dict_size: int = DEFAULT_DICT_SIZE) -> bytes:
    """Compress bytes using a local dictionary + zlib prototype.

    Non-text inputs fall back to the core compressor with ``method="auto"``.
    """
    if not _is_text(data):
        return core_compress(data, method="auto")

    text = data.decode("utf-8")
    dict_tokens = _build_dictionary(text, dict_size)
    if not dict_tokens:
        return zlib.compress(text.encode("utf-8"), level=6)

    dict_tokens = dict_tokens[:255]
    token_to_idx = {t: i for i, t in enumerate(dict_tokens)}

    out = bytearray()
    parts = _TOKEN_RE.findall(text)
    for p in parts:
        lw = p.lower()
        if lw in token_to_idx and len(p) >= MIN_TOKEN_LEN and p.isalnum():
            idx = token_to_idx[lw]
            out.append(0x01)
            out.append(idx)
        else:
            b = p.encode("utf-8")
            out.append(0x00)
            out.extend(len(b).to_bytes(2, "big"))
            out.extend(b)

    header = bytearray()
    header.append(len(dict_tokens))
    for token in dict_tokens:
        tb = token.encode("utf-8")
        header.extend(len(tb).to_bytes(2, "big"))
        header.extend(tb)

    body = bytes(header) + bytes(out)
    return zlib.compress(body, level=6)


def decompress_text(payload: bytes) -> bytes:
    """Decompress a payload produced by :func:`compress_text`."""
    try:
        body = zlib.decompress(payload)
    except Exception:
        return core_decompress(payload)

    if len(body) < 1:
        return body

    i = 0
    n = body[i]
    i += 1
    tokens: List[str] = []
    for _ in range(n):
        if i + 2 > len(body):
            raise ValueError("invalid Sx header")
        l = int.from_bytes(body[i : i + 2], "big")
        i += 2
        if i + l > len(body):
            raise ValueError("invalid Sx header token length")
        token = body[i : i + l].decode("utf-8")
        i += l
        tokens.append(token)

    out_chunks: List[bytes] = []
    while i < len(body):
        typ = body[i]
        i += 1
        if typ == 0x01:
            if i >= len(body):
                raise ValueError("invalid Sx body ref")
            idx = body[i]
            i += 1
            if idx >= len(tokens):
                raise ValueError("invalid Sx dict index")
            out_chunks.append(tokens[idx].encode("utf-8"))
        elif typ == 0x00:
            if i + 2 > len(body):
                raise ValueError("invalid Sx literal length")
            l = int.from_bytes(body[i : i + 2], "big")
            i += 2
            if i + l > len(body):
                raise ValueError("invalid Sx literal payload")
            out_chunks.append(body[i : i + l])
            i += l
        else:
            raise ValueError("unknown Sx segment type")

    return b"".join(out_chunks)


def compress(data: bytes) -> bytes:
    """Compatibility wrapper used by Sx prototype tests."""
    return compress_text(data)


def decompress(payload: bytes) -> bytes:
    """Compatibility wrapper used by Sx prototype tests."""
    return decompress_text(payload)
