"""Semantic Grain (Sg) codec implementation.

This module prefers the high-performance Grain codec from the original
AURA implementation (BRIO via CompressionEngine) when available, and
falls back to a hash-chain-based LZ codec otherwise.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import struct

try:  # pragma: no cover - best-effort integration
    from aura_compression import compression_engine, templates
    from aura_compression.semantic_codecs import SemanticGrainCodec as AuraGrainCodec

    _TEMPLATE_LIB = templates.TemplateLibrary(custom_templates=None)
    _ENGINE = compression_engine.CompressionEngine(template_library=_TEMPLATE_LIB)
    _AURA_GRAIN: Optional[AuraGrainCodec] = AuraGrainCodec(_ENGINE)
    # Quick self-test; if it fails, disable AURA grain.
    try:
        _test_payload, _ = _AURA_GRAIN.compress("grain-self-test")
        _test_text, _ = _AURA_GRAIN.decompress(_test_payload)
        if _test_text != "grain-self-test":
            _AURA_GRAIN = None
    except Exception:
        _AURA_GRAIN = None
except Exception:  # pragma: no cover
    _AURA_GRAIN = None


class SemanticGrainCodec:
    """Grain-oriented compressor for dense, repetitive data."""

    def __init__(self, min_match: int = 3, max_match: int = 255, default_window: int = 1024) -> None:
        self.min_match = min_match
        self.max_match = max_match
        self.default_window = default_window

    def _build_hash_chain(self, data: bytes, window: int) -> Dict[int, List[int]]:
        """Build hash chain for fast prefix matching."""
        hash_chain: Dict[int, List[int]] = {}
        length = len(data)
        if length < 3:
            return {}
        for i in range(length - 2):
            prefix = struct.unpack("!I", data[i : i + 3] + b"\0")[0]  # 3-byte hash
            if prefix not in hash_chain:
                hash_chain[prefix] = []
            hash_chain[prefix].append(i)
            # Cap chain length for small data efficiency
            if len(hash_chain[prefix]) > 32:
                hash_chain[prefix].pop(0)
        return hash_chain

    def compress(self, data: bytes) -> bytes:
        """Compress data using hash-chain LZ with typed tokens."""
        if not data:
            return b""

        substituted = data  # Placeholder: template substitution can be added later.
        compressed = bytearray()

        i = 0
        data_len = len(substituted)
        window = min(self.default_window, data_len)  # Adaptive for small data

        hash_chain = self._build_hash_chain(substituted, window)

        while i < data_len:
            if data_len - i < self.min_match:  # Tail: emit literals safely
                compressed.append(0x00)  # Literal type
                compressed.append(data_len - i)  # Len
                compressed.extend(substituted[i:])
                break

            # Get candidates via hash (only if we have 3 bytes available)
            candidates: List[int] = []
            if i + 3 <= data_len:
                prefix_data = substituted[i : i + 3] + b"\0"
                prefix = struct.unpack("!I", prefix_data)[0]
                candidates = hash_chain.get(prefix, [])

            best_len = 0
            best_offset = 0

            for cand in candidates:
                if cand >= i or i - cand > window:
                    continue
                match_len = 0
                while (
                    match_len < self.max_match
                    and i + match_len < data_len
                    and substituted[cand + match_len] == substituted[i + match_len]
                ):
                    match_len += 1
                if match_len > best_len and match_len >= self.min_match:
                    best_len = match_len
                    best_offset = i - cand

            if best_len >= self.min_match:
                # Encode match: type 0x01 + offset (2 bytes) + len (1 byte)
                compressed.append(0x01)
                compressed.extend(struct.pack("!HB", best_offset, best_len))
                i += best_len
            else:
                # Literal: type 0x00 + len (1) + data
                lit_len = 1
                compressed.append(0x00)
                compressed.append(lit_len)
                compressed.append(substituted[i])
                i += 1

            # Update hash chain when at least 3 bytes remain.
            if i + 3 <= data_len:
                new_prefix_data = substituted[i : i + 3] + b"\0"
                new_prefix = struct.unpack("!I", new_prefix_data)[0]
                if new_prefix not in hash_chain:
                    hash_chain[new_prefix] = []
                hash_chain[new_prefix].append(i)
                if len(hash_chain[new_prefix]) > 32:
                    hash_chain[new_prefix].pop(0)

        return bytes(compressed)

    def decompress(self, compressed: bytes) -> bytes:
        """Decompress data previously compressed by :meth:`compress`."""
        if not compressed:
            return b""

        raw_decomp = bytearray()
        i = 0
        comp_len = len(compressed)

        while i < comp_len:
            typ = compressed[i]
            i += 1
            if typ == 0x01:  # Match
                if i + 3 > comp_len:
                    raise ValueError("Invalid match token")
                offset, length = struct.unpack("!HB", compressed[i : i + 3])
                i += 3
                start = len(raw_decomp) - offset
                if start < 0:
                    raise ValueError("Invalid offset in match")
                for _ in range(length):
                    raw_decomp.append(raw_decomp[start])
                    start += 1
            elif typ == 0x00:  # Literal
                if i >= comp_len:
                    raise ValueError("Missing literal length")
                lit_len = compressed[i]
                i += 1
                if i + lit_len > comp_len:
                    raise ValueError("Invalid literal length")
                raw_decomp.extend(compressed[i : i + lit_len])
                i += lit_len
            else:
                raise ValueError(f"Unknown type {typ}")

        return bytes(raw_decomp)


_SG_CODEC = SemanticGrainCodec()


def compress(data: bytes) -> bytes:
    """Module-level helper for Sg compression."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    if _AURA_GRAIN is not None:
        try:
            text = bytes(data).decode("utf-8")
        except UnicodeDecodeError:
            return _SG_CODEC.compress(bytes(data))
        try:
            compressed, _meta = _AURA_GRAIN.compress(text)
            return compressed
        except Exception:
            return _SG_CODEC.compress(bytes(data))

    return _SG_CODEC.compress(bytes(data))


def decompress(compressed: bytes) -> bytes:
    """Module-level helper for Sg decompression."""
    if not isinstance(compressed, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    if _AURA_GRAIN is not None:
        try:
            text, _meta = _AURA_GRAIN.decompress(bytes(compressed))
            if isinstance(text, str):
                return text.encode("utf-8")
            return bytes(text)
        except Exception:
            return _SG_CODEC.decompress(bytes(compressed))

    return _SG_CODEC.decompress(bytes(compressed))
