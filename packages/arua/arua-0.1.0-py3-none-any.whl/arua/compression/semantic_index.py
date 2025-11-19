"""Semantic Index (Si) codec.

Si encodes global/index metadata (document IDs, section IDs, shard IDs, offsets)
for audit and retrieval. This codec uses a fixed binary layout for index metadata
that is independent of the underlying content codec.

The wire format embeds index metadata (doc_id, section_id, shard_id, offset) as
a compact fixed-size binary structure alongside the compressed payload. This binds
Sv/Sq/Sm/Su payloads into larger corpora and indexes, helping routing components
choose which storage/search component should handle a message.

Binary layout (v1, big-endian):
    [u64 doc_id][u32 section_id][u32 shard_id][u64 offset]

Example:
    data = b"document chunk"
    index = IndexMetadata(doc_id=12345, section_id=42, shard_id=3, offset=1024)
    compressed = compress(data, index)
    original, idx = decompress(compressed)
    # idx.doc_id == 12345, idx.section_id == 42, etc.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

from .core import compress as core_compress
from .core import decompress as core_decompress

_INDEX_STRUCT = struct.Struct(">QIIQ")


@dataclass(frozen=True)
class IndexMetadata:
    """Simple index metadata for a compressed chunk."""

    doc_id: int
    section_id: int
    shard_id: int
    offset: int


def encode_index(meta: IndexMetadata) -> bytes:
    """Encode IndexMetadata into a fixed-size binary representation."""
    return _INDEX_STRUCT.pack(
        int(meta.doc_id),
        int(meta.section_id),
        int(meta.shard_id),
        int(meta.offset),
    )


def decode_index(payload: bytes) -> IndexMetadata:
    """Decode IndexMetadata from a fixed-size binary representation."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_index() expects a bytes-like object")
    if len(payload) != _INDEX_STRUCT.size:
        raise ValueError("invalid index payload size")
    doc_id, section_id, shard_id, offset = _INDEX_STRUCT.unpack(payload)
    return IndexMetadata(
        doc_id=doc_id,
        section_id=section_id,
        shard_id=shard_id,
        offset=offset,
    )


def compress(data: bytes, index: IndexMetadata | None = None) -> bytes:
    """Compress data with optional index metadata.

    Args:
        data: The payload to compress.
        index: Optional IndexMetadata with document/section/shard/offset information.
               If None, zero values are encoded.

    Returns:
        Compressed payload with embedded index metadata.

    The wire format is:
        [24-byte index_metadata][compressed_data]

    Where index_metadata is the fixed-size binary encoding (8+4+4+8 = 24 bytes),
    and compressed_data is the core compressed payload.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    # Encode index metadata
    if index is None:
        index = IndexMetadata(doc_id=0, section_id=0, shard_id=0, offset=0)
    index_blob = encode_index(index)

    # Compress the actual data payload
    compressed_data = core_compress(data, method="auto")

    # Pack: [fixed-size index][compressed_data]
    return index_blob + compressed_data


def decompress(payload: bytes) -> tuple[bytes, IndexMetadata]:
    """Decompress an Si payload and extract index metadata.

    Args:
        payload: The compressed payload with embedded index metadata.

    Returns:
        A tuple of (decompressed_data, index_metadata).

    Raises:
        ValueError: If the payload is malformed.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    payload = bytes(payload)

    # Need at least 24 bytes for index metadata
    if len(payload) < _INDEX_STRUCT.size:
        raise ValueError(
            f"Si payload too short (need at least {_INDEX_STRUCT.size} bytes)"
        )

    # Extract index metadata and compressed data
    index_blob = payload[: _INDEX_STRUCT.size]
    compressed_data = payload[_INDEX_STRUCT.size :]

    # Decode index
    index = decode_index(index_blob)

    # Decompress data
    data = core_decompress(compressed_data)

    return data, index

