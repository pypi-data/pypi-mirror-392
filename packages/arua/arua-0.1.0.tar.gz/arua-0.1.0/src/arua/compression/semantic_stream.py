"""Semantic Wave/Stream (Sw) codec.

Sw encodes streaming/windowing metadata alongside compressed stream data.
This codec is designed for time-series, audio, and continuous data streams,
storing stream metadata (sample_rate, window_size, format) separately from
the compressed stream data.

The wire format embeds stream metadata as JSON alongside compressed stream data:
    [2-byte metadata_blob_length][metadata_blob][compressed_stream_data]

Example:
    stream_data = b"..."  # compressed stream windows
    metadata = {"sample_rate": 16000, "window_size": 4096, "format": "pcm"}
    compressed = compress(stream_data, metadata=metadata)
    data, decoded_metadata = decompress(compressed)
"""

from __future__ import annotations

import json
import struct
from typing import Any, Dict, Iterable, Iterator, List

from .core import compress as core_compress
from .core import decompress as core_decompress

_LENGTH_STRUCT = struct.Struct(">I")  # unsigned 32-bit big-endian
_COMPONENT_STRUCT = struct.Struct(">h")  # signed 16-bit big-endian
_MAX_I16 = 32767
_MIN_I16 = -32768


def _quantize_sample(value: float) -> int:
    """Quantize a float into a signed 16-bit integer."""
    scaled = int(round(value * _MAX_I16))
    if scaled > _MAX_I16:
        scaled = _MAX_I16
    if scaled < _MIN_I16:
        scaled = _MIN_I16
    return scaled


def encode_wave(samples: Iterable[float]) -> bytes:
    """Encode a wave/stream of samples into a compact binary form.

    Args:
        samples: Iterable of floats representing the signal over time.

    Returns:
        Bytes payload with length, base sample and delta-encoded
        subsequent samples, all quantized to signed 16-bit.
    """
    vals: List[float] = list(samples)
    length = len(vals)
    out = bytearray()
    out.extend(_LENGTH_STRUCT.pack(length))
    if length == 0:
        return bytes(out)

    base_q = _quantize_sample(float(vals[0]))
    out.extend(_COMPONENT_STRUCT.pack(base_q))

    prev_q = base_q
    for value in vals[1:]:
        q = _quantize_sample(float(value))
        delta = q - prev_q
        if delta > _MAX_I16:
            delta = _MAX_I16
        if delta < _MIN_I16:
            delta = _MIN_I16
        out.extend(_COMPONENT_STRUCT.pack(delta))
        prev_q = q
    return bytes(out)


def decode_wave(payload: bytes) -> list[float]:
    """Decode a wave/stream from the compact binary representation."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_wave() expects a bytes-like object")
    data = memoryview(payload)
    if len(data) < _LENGTH_STRUCT.size:
        raise ValueError("payload too short for wave length")
    (length,) = _LENGTH_STRUCT.unpack_from(data, 0)
    if length == 0:
        if len(data) != _LENGTH_STRUCT.size:
            raise ValueError("extra data after empty wave header")
        return []

    expected_size = _LENGTH_STRUCT.size + length * _COMPONENT_STRUCT.size
    if len(data) != expected_size:
        raise ValueError("payload size does not match encoded length")

    offset = _LENGTH_STRUCT.size
    (base_q,) = _COMPONENT_STRUCT.unpack_from(data, offset)
    offset += _COMPONENT_STRUCT.size
    samples_q: list[int] = [base_q]
    current_q = base_q
    for _ in range(length - 1):
        (delta,) = _COMPONENT_STRUCT.unpack_from(data, offset)
        offset += _COMPONENT_STRUCT.size
        current_q += delta
        samples_q.append(current_q)
    return [q / _MAX_I16 for q in samples_q]


DEFAULT_WINDOW = 64 * 1024


def compress_stream(data: bytes, window_size: int = DEFAULT_WINDOW) -> bytes:
    """Chunk `data` into windows and compress each window with zlib.

    Returns a simple chunked format: [4B chunk_id][4B compressed_len][payload]...
    """
    import zlib

    out = bytearray()
    i = 0
    chunk_id = 0
    while i < len(data):
        window = data[i : i + window_size]
        compressed = zlib.compress(window, level=6)
        out.extend(chunk_id.to_bytes(4, "big"))
        out.extend(len(compressed).to_bytes(4, "big"))
        out.extend(compressed)
        i += window_size
        chunk_id += 1
    return bytes(out)


def decompress_stream(payload: bytes) -> bytes:
    """Decompress a payload produced by :func:`compress_stream`."""
    import zlib

    i = 0
    out = bytearray()
    data = memoryview(payload)
    while i < len(data):
        if i + 8 > len(data):
            raise ValueError("invalid stream header")
        length = int.from_bytes(data[i + 4 : i + 8], "big")
        i += 8
        if i + length > len(data):
            raise ValueError("invalid chunk length")
        compressed = bytes(data[i : i + length])
        i += length
        out.extend(zlib.decompress(compressed))
    return bytes(out)


def iter_decompressed_windows(payload: bytes) -> Iterator[bytes]:
    """Yield decompressed windows from a chunked stream payload."""
    import zlib

    i = 0
    data = memoryview(payload)
    while i < len(data):
        if i + 8 > len(data):
            raise ValueError("invalid stream header")
        length = int.from_bytes(data[i + 4 : i + 8], "big")
        i += 8
        compressed = bytes(data[i : i + length])
        i += length
        yield zlib.decompress(compressed)




def compress(data: bytes, metadata: Dict[str, Any] | None = None) -> bytes:
    """Compress stream data with optional metadata.

    Args:
        data: The stream payload to compress (typically compressed windows).
        metadata: Optional dictionary of stream metadata (sample_rate, window_size, format, etc.).
                  If None, an empty metadata dict is encoded.

    Returns:
        Compressed payload with embedded stream metadata.

    The wire format is:
        [2-byte metadata_blob_length][metadata_blob][compressed_data]

    Where metadata_blob is JSON-encoded stream metadata, and compressed_data
    is the core compressed payload.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    # Encode stream metadata
    if metadata is None:
        metadata = {}
    metadata_blob = json.dumps(metadata, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    # Enforce metadata blob size limit (64KB max for 2-byte length prefix)
    if len(metadata_blob) > 0xFFFF:
        raise ValueError("stream metadata too large (max 65535 bytes)")

    # Compress the actual data payload
    compressed_data = core_compress(bytes(data), method="auto")

    # Pack: [2-byte length][metadata_blob][compressed_data]
    metadata_length = len(metadata_blob)
    length_bytes = bytes([(metadata_length >> 8) & 0xFF, metadata_length & 0xFF])

    return length_bytes + metadata_blob + compressed_data


def decompress(payload: bytes) -> tuple[bytes, Dict[str, Any]]:
    """Decompress an Sw payload and extract stream metadata.

    Args:
        payload: The compressed payload with embedded stream metadata.

    Returns:
        A tuple of (decompressed_data, metadata).

    Raises:
        TypeError: If payload is not bytes-like.
        ValueError: If payload is malformed.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    data = bytes(payload)
    if len(data) < 2:
        raise ValueError("Sw payload too short for length header")

    # Read 2-byte metadata blob length
    metadata_length = (data[0] << 8) | data[1]

    # Validate we have enough data
    if len(data) < 2 + metadata_length:
        raise ValueError("Sw payload truncated before metadata blob")

    # Extract metadata blob and compressed data
    metadata_blob = data[2 : 2 + metadata_length]
    compressed_data = data[2 + metadata_length :]

    # Decode stream metadata
    try:
        metadata = json.loads(metadata_blob.decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid Sw payload JSON") from exc

    if not isinstance(metadata, dict):
        raise ValueError("Sw payload must contain a JSON object")

    # Decompress data
    decompressed_data = core_decompress(compressed_data)

    return decompressed_data, metadata

