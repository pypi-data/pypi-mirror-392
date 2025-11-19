"""Semantic Node (Sn) codec.

Sn describes where in a physical or logical topology a message originates or
should be processed (node/region/rack/cluster role). This codec encodes node IDs,
locality hints, and failure-domain information independent from the content codec.

The wire format embeds topology metadata (cluster, region, zone, node_id, role)
as a compact JSON object alongside the compressed payload. This enables routing,
placement decisions, and failure domain awareness.

Example:
    data = b"distributed payload"
    location = NodeLocation(
        cluster="prod-us",
        region="us-west-2",
        zone="us-west-2a",
        node_id="node-42",
        role="compute"
    )
    compressed = compress(data, location)
    original, node_info = decompress(compressed)
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .core import compress as core_compress
from .core import decompress as core_decompress


@dataclass(frozen=True)
class NodeLocation:
    """Topology metadata for a node."""

    cluster: str
    region: str
    zone: str
    node_id: str
    role: str


def encode_node(location: NodeLocation) -> bytes:
    """Encode NodeLocation into a UTF-8 JSON body."""
    obj = {
        "cluster": location.cluster,
        "region": location.region,
        "zone": location.zone,
        "node_id": location.node_id,
        "role": location.role,
    }
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")


def decode_node(payload: bytes) -> NodeLocation:
    """Decode NodeLocation from a UTF-8 JSON body."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_node() expects a bytes-like object")
    try:
        obj = json.loads(bytes(payload).decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid Sn payload JSON") from exc
    if not isinstance(obj, dict):
        raise ValueError("Sn payload must be a JSON object")
    return NodeLocation(
        cluster=str(obj.get("cluster", "")),
        region=str(obj.get("region", "")),
        zone=str(obj.get("zone", "")),
        node_id=str(obj.get("node_id", "")),
        role=str(obj.get("role", "")),
    )


def compress(data: bytes, location: NodeLocation | None = None) -> bytes:
    """Compress data with optional node location metadata.

    Args:
        data: The payload to compress.
        location: Optional NodeLocation with topology information.
                  If None, empty location fields are encoded.

    Returns:
        Compressed payload with embedded node metadata.

    The wire format is:
        [2-byte node_blob_length][node_blob][compressed_data]

    Where node_blob is JSON-encoded location metadata, and compressed_data
    is the core compressed payload.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    # Encode node location metadata
    if location is None:
        location = NodeLocation(
            cluster="", region="", zone="", node_id="", role=""
        )
    node_blob = encode_node(location)

    # Enforce node blob size limit (64KB max for 2-byte length prefix)
    if len(node_blob) > 0xFFFF:
        raise ValueError("node metadata too large (max 65535 bytes)")

    # Compress the actual data payload
    compressed_data = core_compress(data, method="auto")

    # Pack: [2-byte length][node_blob][compressed_data]
    node_length = len(node_blob)
    length_bytes = bytes([(node_length >> 8) & 0xFF, node_length & 0xFF])

    return length_bytes + node_blob + compressed_data


def decompress(payload: bytes) -> tuple[bytes, NodeLocation]:
    """Decompress an Sn payload and extract node location metadata.

    Args:
        payload: The compressed payload with embedded node metadata.

    Returns:
        A tuple of (decompressed_data, node_location).

    Raises:
        ValueError: If the payload is malformed.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    payload = bytes(payload)

    # Need at least 2 bytes for length prefix
    if len(payload) < 2:
        raise ValueError("Sn payload too short (need at least 2 bytes)")

    # Read 2-byte node blob length
    node_length = (payload[0] << 8) | payload[1]

    # Validate we have enough data
    if len(payload) < 2 + node_length:
        raise ValueError(
            f"Sn payload truncated: expected {2 + node_length} bytes, got {len(payload)}"
        )

    # Extract node blob and compressed data
    node_blob = payload[2 : 2 + node_length]
    compressed_data = payload[2 + node_length :]

    # Decode node location
    location = decode_node(node_blob)

    # Decompress data
    data = core_decompress(compressed_data)

    return data, location

