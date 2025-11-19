"""Semantic Learned (Sl) codec (CPU placeholder).

This module encodes simple metadata about a learned/ML codec alongside
compressed payload bytes. It is intended as a lightweight helper for
Sl-labelled payloads without changing the compact semantic header.

Wire format:

    [2B meta_len][meta_blob][compressed_data]

Where:
    * meta_blob is a UTF-8 JSON object describing model/latent metadata.
    * compressed_data is produced by :mod:`arua.compression.core`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from .core import compress as core_compress
from .core import decompress as core_decompress


@dataclass(frozen=True)
class LearnedMetadata:
    """Metadata describing a learned codec configuration."""

    model_name: str
    version: str
    latent_dim: int
    has_residual: bool = False
    extra: Dict[str, Any] | None = None


def encode_learned(meta: LearnedMetadata) -> bytes:
    """Encode LearnedMetadata into a UTF-8 JSON body."""
    obj: Dict[str, Any] = {
        "model_name": meta.model_name,
        "version": meta.version,
        "latent_dim": meta.latent_dim,
        "has_residual": meta.has_residual,
        "extra": meta.extra or {},
    }
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")


def decode_learned(payload: bytes) -> LearnedMetadata:
    """Decode LearnedMetadata from a UTF-8 JSON body."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_learned() expects a bytes-like object")
    try:
        obj = json.loads(bytes(payload).decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid Sl payload JSON") from exc
    if not isinstance(obj, dict):
        raise ValueError("Sl payload must be a JSON object")
    model_name = str(obj.get("model_name", "unknown"))
    version = str(obj.get("version", "0"))
    latent_dim = int(obj.get("latent_dim", 0))
    has_residual = bool(obj.get("has_residual", False))
    extra_field = obj.get("extra") or {}
    if not isinstance(extra_field, dict):
        raise ValueError("Sl 'extra' field must be a JSON object")
    extra: Dict[str, Any] = dict(extra_field)
    return LearnedMetadata(
        model_name=model_name,
        version=version,
        latent_dim=latent_dim,
        has_residual=has_residual,
        extra=extra,
    )


def compress(data: bytes, meta: LearnedMetadata | None = None) -> bytes:
    """Compress data with learned codec metadata."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")
    if meta is None:
        meta = LearnedMetadata(model_name="unknown", version="0", latent_dim=0)

    meta_blob = encode_learned(meta)
    if len(meta_blob) > 0xFFFF:
        raise ValueError("learned metadata too large (max 65535 bytes)")

    compressed_data = core_compress(bytes(data), method="auto")

    meta_len = len(meta_blob)
    length_bytes = bytes([(meta_len >> 8) & 0xFF, meta_len & 0xFF])
    return length_bytes + meta_blob + compressed_data


def decompress(payload: bytes) -> Tuple[bytes, LearnedMetadata]:
    """Decompress an Sl payload and extract learned codec metadata."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    payload = bytes(payload)
    if len(payload) < 2:
        raise ValueError("Sl payload too short (need at least 2 bytes)")

    meta_len = (payload[0] << 8) | payload[1]
    if len(payload) < 2 + meta_len:
        raise ValueError(
            f"Sl payload truncated: expected {2 + meta_len} bytes, got {len(payload)}"
        )

    meta_blob = payload[2 : 2 + meta_len]
    compressed_data = payload[2 + meta_len :]

    meta = decode_learned(meta_blob)
    data = core_decompress(compressed_data)
    return data, meta

