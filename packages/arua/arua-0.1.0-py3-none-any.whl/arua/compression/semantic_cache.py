"""Semantic Cache (Ss) codec.

Ss implements cache-based substitution compression: it identifies frequently
occurring patterns (tokens, phrases, byte sequences) and replaces them with
short references to a dictionary. This is particularly effective for LLM
workloads where the same tokens/phrases appear repeatedly.

Wire format:

    [2B dict_len][dict_blob][4B data_len][compressed_data_with_refs]

Where:
    * dict_blob is a UTF-8 JSON array of cache entries (strings or hex-encoded bytes)
    * compressed_data_with_refs contains the data with frequent patterns replaced
      by references (format: 0xFF [2B reference_id])

For optimal compression:
    - Build frequency table of substrings
    - Create dictionary of most frequent patterns (up to 65535 entries)
    - Replace patterns with references in data
    - Emit dictionary + compressed data

Cache hit rates in LLM inference: 50-80% on repeated prompts, system messages,
function signatures, and common tokens.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .core import compress as core_compress
from .core import decompress as core_decompress

# Constants
CACHE_MARKER = 0xFF  # Signals start of cache reference
MIN_PATTERN_LENGTH = 4  # Minimum bytes to consider for caching
MAX_DICT_ENTRIES = 256  # Keep dictionary small for fast lookup
MIN_FREQUENCY = 2  # Minimum occurrences to add to dictionary


@dataclass(frozen=True)
class CacheMetadata:
    """Metadata for cache-based compression."""

    dict_size: int
    original_size: int
    compressed_size: int
    hit_rate: float  # Percentage of bytes substituted
    extra: Dict[str, Any] | None = None


def _build_frequency_table(data: bytes, min_length: int = MIN_PATTERN_LENGTH) -> Counter:
    """Build frequency table of byte patterns in data.

    Scans data for all substrings of length min_length to 32 bytes
    and counts their occurrences.
    """
    freq_table: Counter = Counter()

    # Scan with sliding window for different pattern lengths
    # Cap at 32 bytes max to avoid excessive pattern scanning
    max_pattern_len = min(33, len(data) + 1)
    for pattern_len in range(min_length, max_pattern_len):
        for i in range(len(data) - pattern_len + 1):
            pattern = bytes(data[i : i + pattern_len])
            freq_table[pattern] += 1

    return freq_table


def _build_dictionary(
    freq_table: Counter, max_entries: int = MAX_DICT_ENTRIES, min_freq: int = MIN_FREQUENCY
) -> Dict[bytes, int]:
    """Build dictionary of most frequent patterns.

    Returns mapping: pattern -> reference_id
    """
    # Filter by minimum frequency
    frequent = {pattern: count for pattern, count in freq_table.items() if count >= min_freq}

    # Sort by compression value (frequency * length - overhead)
    # Each substitution saves (pattern_length - 3) bytes (3 = marker + 2B ref)
    value_scored = [
        (pattern, freq * (len(pattern) - 3)) for pattern, freq in frequent.items() if len(pattern) > 3
    ]
    value_scored.sort(key=lambda x: x[1], reverse=True)

    # Take top entries
    dictionary = {}
    for i, (pattern, _) in enumerate(value_scored[:max_entries]):
        dictionary[pattern] = i

    return dictionary


def _substitute_patterns(data: bytes, dictionary: Dict[bytes, int]) -> bytearray:
    """Replace patterns in data with cache references.

    Format: 0xFF [ref_id_hi] [ref_id_lo]
    """
    result = bytearray()
    i = 0

    # Sort patterns by length (longest first) to avoid partial matches
    sorted_patterns = sorted(dictionary.keys(), key=len, reverse=True)

    while i < len(data):
        matched = False

        # Try to match longest pattern first
        for pattern in sorted_patterns:
            if data[i : i + len(pattern)] == pattern:
                ref_id = dictionary[pattern]
                # Emit cache reference: 0xFF [hi] [lo]
                result.append(CACHE_MARKER)
                result.append((ref_id >> 8) & 0xFF)
                result.append(ref_id & 0xFF)
                i += len(pattern)
                matched = True
                break

        if not matched:
            # Literal byte
            byte_val = data[i]
            if byte_val == CACHE_MARKER:
                # Escape cache marker: 0xFF 0xFF 0xFF
                result.extend([CACHE_MARKER, CACHE_MARKER, CACHE_MARKER])
            else:
                result.append(byte_val)
            i += 1

    return result


def _restore_patterns(data: bytes, dictionary: List[bytes]) -> bytearray:
    """Restore patterns from cache references."""
    result = bytearray()
    i = 0

    while i < len(data):
        if data[i] == CACHE_MARKER:
            if i + 2 < len(data):
                # Check for escaped marker
                if data[i + 1] == CACHE_MARKER and data[i + 2] == CACHE_MARKER:
                    result.append(CACHE_MARKER)
                    i += 3
                else:
                    # Cache reference
                    ref_id = (data[i + 1] << 8) | data[i + 2]
                    if ref_id < len(dictionary):
                        result.extend(dictionary[ref_id])
                        i += 3
                    else:
                        raise ValueError(f"Invalid cache reference: {ref_id} (dict size: {len(dictionary)})")
            else:
                raise ValueError("Truncated cache reference at end of data")
        else:
            result.append(data[i])
            i += 1

    return result


def compress(
    data: bytes, min_pattern_length: int = MIN_PATTERN_LENGTH, max_dict_size: int = MAX_DICT_ENTRIES
) -> bytes:
    """Compress data using cache-based substitution.

    Wire format: [2B dict_len][dict_blob][4B data_len][substituted_data]
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    raw = bytes(data)
    original_size = len(raw)

    # Build frequency table
    freq_table = _build_frequency_table(raw, min_length=min_pattern_length)

    # Build dictionary of frequent patterns
    dictionary = _build_dictionary(freq_table, max_entries=max_dict_size)

    if not dictionary:
        # No patterns found, use core compression
        compressed = core_compress(raw, method="auto")
        # Emit empty dictionary (binary format: num_entries=0)
        dict_blob = bytes([0, 0])  # num_entries = 0
        dict_len = len(dict_blob)
        data_len = len(compressed)
        return bytes(
            [(dict_len >> 8) & 0xFF, dict_len & 0xFF]
            + list(dict_blob)
            + [(data_len >> 24) & 0xFF, (data_len >> 16) & 0xFF, (data_len >> 8) & 0xFF, data_len & 0xFF]
            + list(compressed)
        )

    # Substitute patterns with references
    substituted = _substitute_patterns(raw, dictionary)
    compressed_size = len(substituted)

    # Calculate hit rate
    bytes_saved = original_size - compressed_size
    hit_rate = (bytes_saved / original_size) * 100 if original_size > 0 else 0.0

    # Serialize dictionary as binary: [num_entries:2B][len:2B pattern:bytes]...
    dict_blob = bytearray()
    dict_blob.extend([(len(dictionary) >> 8) & 0xFF, len(dictionary) & 0xFF])

    # Sort by ref_id to ensure consistent ordering
    sorted_patterns = sorted(dictionary.items(), key=lambda x: x[1])
    for pattern, ref_id in sorted_patterns:
        pattern_len = len(pattern)
        if pattern_len > 0xFFFF:
            raise ValueError(f"Pattern too large: {pattern_len} bytes")
        dict_blob.extend([(pattern_len >> 8) & 0xFF, pattern_len & 0xFF])
        dict_blob.extend(pattern)

    dict_blob = bytes(dict_blob)

    if len(dict_blob) > 0xFFFF:
        raise ValueError("Dictionary too large (max 65535 bytes)")

    # Compress the substituted data with core compressor
    final_compressed = core_compress(bytes(substituted), method="auto")

    # Check if dictionary approach actually saves bytes
    dict_len = len(dict_blob)
    data_len = len(final_compressed)
    total_with_dict = 2 + dict_len + 4 + data_len

    # Compare with plain core compression
    plain_compressed = core_compress(raw, method="auto")
    plain_total = 2 + 2 + 4 + len(plain_compressed)  # Empty dict overhead

    if total_with_dict >= plain_total:
        # Dictionary doesn't help, use plain compression
        dict_blob = bytearray()
        dict_blob.extend([0, 0])  # num_entries = 0
        dict_blob = bytes(dict_blob)
        dict_len = len(dict_blob)
        data_len = len(plain_compressed)

        result = bytearray()
        result.extend([(dict_len >> 8) & 0xFF, dict_len & 0xFF])
        result.extend(dict_blob)
        result.extend(
            [(data_len >> 24) & 0xFF, (data_len >> 16) & 0xFF, (data_len >> 8) & 0xFF, data_len & 0xFF]
        )
        result.extend(plain_compressed)
        return bytes(result)

    # Dictionary helps, use it
    result = bytearray()
    result.extend([(dict_len >> 8) & 0xFF, dict_len & 0xFF])
    result.extend(dict_blob)
    result.extend(
        [(data_len >> 24) & 0xFF, (data_len >> 16) & 0xFF, (data_len >> 8) & 0xFF, data_len & 0xFF]
    )
    result.extend(final_compressed)

    return bytes(result)


def decompress(payload: bytes) -> Tuple[bytes, CacheMetadata]:
    """Decompress Ss payload and extract cache metadata."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    payload = bytes(payload)
    if len(payload) < 6:
        raise ValueError("Ss payload too short (need at least 6 bytes)")

    # Parse dictionary length
    dict_len = (payload[0] << 8) | payload[1]
    if len(payload) < 2 + dict_len + 4:
        raise ValueError(f"Ss payload truncated: expected {2 + dict_len + 4} bytes header")

    # Parse dictionary (binary format: [num_entries:2B][len:2B pattern:bytes]...)
    dict_blob = payload[2 : 2 + dict_len]

    if len(dict_blob) < 2:
        raise ValueError("Dictionary blob too short")

    num_entries = (dict_blob[0] << 8) | dict_blob[1]
    dictionary = []
    offset_in_dict = 2

    for _ in range(num_entries):
        if offset_in_dict + 2 > len(dict_blob):
            raise ValueError("Dictionary truncated while reading pattern length")

        pattern_len = (dict_blob[offset_in_dict] << 8) | dict_blob[offset_in_dict + 1]
        offset_in_dict += 2

        if offset_in_dict + pattern_len > len(dict_blob):
            raise ValueError(f"Dictionary truncated while reading pattern data")

        pattern = dict_blob[offset_in_dict : offset_in_dict + pattern_len]
        dictionary.append(bytes(pattern))
        offset_in_dict += pattern_len

    # Parse data length
    offset = 2 + dict_len
    data_len = (
        (payload[offset] << 24) | (payload[offset + 1] << 16) | (payload[offset + 2] << 8) | payload[offset + 3]
    )
    offset += 4

    if len(payload) < offset + data_len:
        raise ValueError(f"Ss payload truncated: expected {offset + data_len} bytes total")

    compressed_data = payload[offset : offset + data_len]

    # Decompress
    substituted_data = core_decompress(compressed_data)

    # Restore patterns (skip if dictionary is empty)
    if dictionary:
        restored = _restore_patterns(substituted_data, dictionary)
    else:
        restored = bytearray(substituted_data)

    # Build metadata
    metadata = CacheMetadata(
        dict_size=len(dictionary),
        original_size=len(restored),
        compressed_size=len(payload),
        hit_rate=0.0,  # Unknown on decompression
    )

    return bytes(restored), metadata
