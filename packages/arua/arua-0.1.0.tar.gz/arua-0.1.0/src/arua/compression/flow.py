"""Semantic Flow (Sf) codec implementation.

This module prefers the high-performance Flow codec from the original
AURA implementation (Auralite via CompressionEngine) when available,
and falls back to a small-window LZ-style codec otherwise.
"""
from __future__ import annotations

from typing import Final, Optional

WINDOW_SIZE: Final[int] = 512
MIN_MATCH: Final[int] = 3
MAX_MATCH: Final[int] = 127  # fits in 7 bits

try:  # pragma: no cover - best-effort integration
    from aura_compression import compression_engine, templates
    from aura_compression.semantic_codecs import SemanticFlowCodec

    _TEMPLATE_LIB = templates.TemplateLibrary(custom_templates=None)
    _ENGINE = compression_engine.CompressionEngine(template_library=_TEMPLATE_LIB)
    _AURA_FLOW: Optional[SemanticFlowCodec] = SemanticFlowCodec(_ENGINE)
    # Quick self-test; if it fails, disable AURA flow.
    try:
        _test_payload, _ = _AURA_FLOW.compress("flow-self-test")
        _test_text, _ = _AURA_FLOW.decompress(_test_payload)
        if _test_text != "flow-self-test":
            _AURA_FLOW = None
    except Exception:
        _AURA_FLOW = None
except Exception:  # pragma: no cover - keep local fallback working
    _AURA_FLOW = None


def _find_longest_match(data: bytes, pos: int) -> tuple[int, int]:
    """Find the longest backward match starting at ``pos``."""
    end = len(data)
    window_start = max(0, pos - WINDOW_SIZE)

    best_len = 0
    best_offset = 0

    for candidate in range(window_start, pos):
        length = 0
        while (
            pos + length < end
            and data[candidate + length] == data[pos + length]
            and length < MAX_MATCH
        ):
            length += 1
        if length >= MIN_MATCH and length > best_len:
            best_len = length
            best_offset = pos - candidate
            if best_len == MAX_MATCH:
                break

    if best_len >= MIN_MATCH and best_offset > 0:
        return best_offset, best_len
    return 0, 0


def _compress_fallback(data: bytes) -> bytes:
    """Local small-window LZ-style fallback."""
    if not data:
        return b""

    src = bytes(data)
    out = bytearray()
    pos = 0
    end = len(src)

    while pos < end:
        offset, length = _find_longest_match(src, pos)

        if length >= MIN_MATCH:
            if length > MAX_MATCH:
                length = MAX_MATCH
            header = 0x80 | (length & 0x7F)
            out.append(header)
            out.extend(offset.to_bytes(2, "big"))
            pos += length
        else:
            header = 0x01  # literal run of length 1
            out.append(header)
            out.append(src[pos])
            pos += 1

    return bytes(out)


def _decompress_fallback(payload: bytes) -> bytes:
    """Decompress data produced by the fallback codec."""
    if not payload:
        return b""

    data = bytes(payload)
    out = bytearray()
    pos = 0
    end = len(data)

    while pos < end:
        header = data[pos]
        pos += 1
        is_match = bool(header & 0x80)
        length = header & 0x7F
        if length == 0:
            raise ValueError("invalid token length 0")

        if is_match:
            if pos + 2 > end:
                raise ValueError("truncated match token")
            offset = int.from_bytes(data[pos : pos + 2], "big")
            pos += 2
            if offset == 0 or offset > len(out):
                raise ValueError("invalid match offset")
            start = len(out) - offset
            for _ in range(length):
                out.append(out[start])
                start += 1
        else:
            if pos + length > end:
                raise ValueError("truncated literal token")
            out.extend(data[pos : pos + length])
            pos += length

    return bytes(out)


def compress(data: bytes) -> bytes:
    """Compress data using AURA Flow when available, else fallback."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    if _AURA_FLOW is not None:
        try:
            text = bytes(data).decode("utf-8")
        except UnicodeDecodeError:
            # Non-text payloads fall back to local codec.
            return _compress_fallback(bytes(data))
        try:
            compressed, _meta = _AURA_FLOW.compress(text)
            return compressed
        except Exception:
            # Any failure falls back to local codec.
            return _compress_fallback(bytes(data))

    return _compress_fallback(bytes(data))


def decompress(payload: bytes) -> bytes:
    """Decompress data produced by :func:`compress`."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    if _AURA_FLOW is not None:
        try:
            text, _meta = _AURA_FLOW.decompress(bytes(payload))
            if isinstance(text, str):
                return text.encode("utf-8")
            return bytes(text)
        except Exception:
            return _decompress_fallback(bytes(payload))

    return _decompress_fallback(bytes(payload))
