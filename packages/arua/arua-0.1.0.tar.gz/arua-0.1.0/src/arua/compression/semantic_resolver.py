"""Semantic Resolver (Sr) codec.

Sr encodes routing hints and resolution metadata for codec selection and
orchestration. This codec embeds information about which codec to use next,
fallback strategies, and routing decisions.

The wire format embeds resolution metadata as JSON alongside compressed data:
    [2-byte resolver_blob_length][resolver_blob][compressed_data]

Example:
    hints = {"next_codec": "Sg", "fallback": "Sb", "priority": "high"}
    compressed = compress(b"data", hints=hints)
    data, decoded_hints = decompress(compressed)
"""

from __future__ import annotations

import importlib
import json
from typing import Any, Dict

from . import core as core_mod
from . import flow as sf_mod
from . import grain as sg_mod
from . import semantic as semantic_mod
from .core import compress as core_compress
from .core import decompress as core_decompress
from .semantic_vector import compress_from_floats as sv_compress_from_floats
from .semantic_stream import compress_stream as sw_compress_stream


class UnsupportedCodecError(RuntimeError):
    """Raised when a requested codec label is not supported by the resolver."""


def resolve_and_compress(
    data: bytes | list[float],
    codec_label: str | None = None,
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Serialize a SemanticHeader and route to the chosen codec.

    If ``codec_label`` is ``None``, run auto semantics (let the top-level
    choose). This function returns header+payload identical to
    :func:`semantic.semantic_compress` for supported labels.
    """
    if codec_label is None:
        # Let top-level pick auto (calls Sa/Sb etc.)
        return semantic_mod.semantic_compress(
            data if isinstance(data, (bytes, bytearray)) else bytes(),
            codec="auto",
            domain_id=domain_id,
            template_id=template_id,
        )

    codec = codec_label.lower()
    if codec == "sa":
        return semantic_mod.semantic_compress(
            data if isinstance(data, (bytes, bytearray)) else bytes(),
            codec="Sa",
            domain_id=domain_id,
            template_id=template_id,
        )
    if codec == "sb":
        return semantic_mod.semantic_compress(
            data if isinstance(data, (bytes, bytearray)) else bytes(),
            codec="Sb",
            domain_id=domain_id,
            template_id=template_id,
        )
    if codec == "sf":
        return semantic_mod.semantic_compress(
            data if isinstance(data, (bytes, bytearray)) else bytes(),
            codec="Sf",
            domain_id=domain_id,
            template_id=template_id,
        )
    if codec == "sg":
        return semantic_mod.semantic_compress(
            data if isinstance(data, (bytes, bytearray)) else bytes(),
            codec="Sg",
            domain_id=domain_id,
            template_id=template_id,
        )

    if codec == "sv":
        # Accept a list/tuple of floats or a JSON-encoded list in bytes.
        if isinstance(data, (list, tuple)):
            vals = data
        elif isinstance(data, (bytes, bytearray)):
            try:
                vals = json.loads(bytes(data).decode("utf-8"))
            except Exception:
                vals = None
        else:
            vals = None
        if vals is None:
            # Fallback to Sb via semantic_mod if we cannot interpret input.
            return semantic_mod.semantic_compress(
                data if isinstance(data, (bytes, bytearray)) else bytes(),
                codec="Sb",
                domain_id=domain_id,
                template_id=template_id,
            )
        compressed = sv_compress_from_floats(vals)
        # Wrap the compressed vector in an Sb body for now.
        return semantic_mod.semantic_compress(
            compressed,
            codec="Sb",
            domain_id=domain_id,
            template_id=template_id,
        )

    if codec == "sw":
        # Treat input as raw bytes for streaming compressor.
        if isinstance(data, (bytes, bytearray)):
            compressed = sw_compress_stream(bytes(data))
        else:
            raise UnsupportedCodecError("Sw expects bytes-like input")
        return semantic_mod.semantic_compress(
            compressed,
            codec="Sb",
            domain_id=domain_id,
            template_id=template_id,
        )

    if codec == "sz":
        return semantic_mod.semantic_compress(
            data if isinstance(data, (bytes, bytearray)) else bytes(),
            codec="Sz",
            domain_id=domain_id,
            template_id=template_id,
        )

    if codec == "su":
        return semantic_mod.semantic_compress(
            data if isinstance(data, (bytes, bytearray)) else bytes(),
            codec="Su",
            domain_id=domain_id,
            template_id=template_id,
        )

    raise UnsupportedCodecError(f"unsupported codec label: {codec_label}")


def resolve_and_decompress(payload: bytes) -> bytes:
    """Parse header and route decompression to the right codec."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("payload must be bytes-like")

    header, body = semantic_mod.SemanticHeader.from_bytes(payload)
    cid = header.codec_id

    # Dispatch by codec id; prefer the explicit functions for Sr.
    if cid == semantic_mod.CODEC_ID_SA:
        return semantic_mod.core_decompress(body)
    if cid == semantic_mod.CODEC_ID_SB:
        return semantic_mod.core_decompress(body)
    if cid == semantic_mod.CODEC_ID_SF:
        return sf_mod.decompress(body)
    if cid == semantic_mod.CODEC_ID_SG:
        return sg_mod.decompress(body)

    # Look up codec label for anything else and fall back to core decompression.
    try:
        label = semantic_mod._CODEC_LABELS.get(cid, None)  # type: ignore[attr-defined]
    except Exception:
        label = None
    if label is not None:
        # Future: add dedicated branches for Sv/Sw/Sz/Su.
        pass

    return core_mod.decompress(body)


def compress(data: bytes, hints: Dict[str, Any] | None = None) -> bytes:
    """Compress data with optional routing/resolution hints.

    Args:
        data: The payload to compress.
        hints: Optional dictionary of routing hints (next_codec, fallback, priority, etc.).
               If None, an empty hints dict is encoded.

    Returns:
        Compressed payload with embedded resolver metadata.

    The wire format is:
        [2-byte resolver_blob_length][resolver_blob][compressed_data]

    Where resolver_blob is JSON-encoded routing hints, and compressed_data
    is the core compressed payload.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    # Encode resolver hints
    if hints is None:
        hints = {}
    resolver_blob = json.dumps(hints, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    # Enforce resolver blob size limit (64KB max for 2-byte length prefix)
    if len(resolver_blob) > 0xFFFF:
        raise ValueError("resolver metadata too large (max 65535 bytes)")

    # Compress the actual data payload
    compressed_data = core_compress(bytes(data), method="auto")

    # Pack: [2-byte length][resolver_blob][compressed_data]
    resolver_length = len(resolver_blob)
    length_bytes = bytes([(resolver_length >> 8) & 0xFF, resolver_length & 0xFF])

    return length_bytes + resolver_blob + compressed_data


def decompress(payload: bytes) -> tuple[bytes, Dict[str, Any]]:
    """Decompress an Sr payload and extract routing hints.

    Args:
        payload: The compressed payload with embedded resolver metadata.

    Returns:
        A tuple of (decompressed_data, hints).

    Raises:
        TypeError: If payload is not bytes-like.
        ValueError: If payload is malformed.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    data = bytes(payload)
    if len(data) < 2:
        raise ValueError("Sr payload too short for length header")

    # Read 2-byte resolver blob length
    resolver_length = (data[0] << 8) | data[1]

    # Validate we have enough data
    if len(data) < 2 + resolver_length:
        raise ValueError("Sr payload truncated before resolver blob")

    # Extract resolver blob and compressed data
    resolver_blob = data[2 : 2 + resolver_length]
    compressed_data = data[2 + resolver_length :]

    # Decode resolver hints
    try:
        hints = json.loads(resolver_blob.decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid Sr payload JSON") from exc

    if not isinstance(hints, dict):
        raise ValueError("Sr payload must contain a JSON object")

    # Decompress data
    decompressed_data = core_decompress(compressed_data)

    return decompressed_data, hints
