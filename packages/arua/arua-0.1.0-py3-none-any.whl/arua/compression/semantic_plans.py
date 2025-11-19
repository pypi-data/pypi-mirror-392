"""Mapping from semantic headers to execution plans.

This module translates a :class:`SemanticHeader` into a simple
`SemanticPlan` object that callers (including GPU/TensorRT code)
can use to choose model tier, quantization and sequence limits.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from ..templates import TemplateLibrary

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from .semantic import SemanticHeader


@dataclass
class SemanticPlan:
    """Execution plan derived from a semantic header."""

    codec_label: str
    domain_id: int
    template_id: int
    model_tier: str
    quantization: str
    max_sequence_length: int
    needs_template_lookup: bool
    entropy_bucket: Optional[int] = None


_CODEC_LABELS = {
    0x01: "Sa",
    0x02: "Sb",
    0x03: "Sc",
    0x04: "Sd",
    0x05: "Se",
    0x06: "Sf",
    0x07: "Sg",
    0x08: "Su",
    0x09: "Sh",
    0x0A: "Si",
    0x0B: "Sj",
    0x0C: "Sk",
    0x0D: "Sl",
    0x0E: "Sm",
    0x0F: "Sn",
    0x10: "So",
    0x11: "Sp",
    0x12: "Sq",
    0x13: "Sr",
    0x14: "Ss",
    0x15: "Sv",
    0x16: "Sw",
    0x17: "Sx",
    0x18: "Sy",
    0x19: "Sz",
    0x1A: "St",
}


def _estimate_entropy_bucket(data: bytes) -> int:
    """Estimate a coarse entropy bucket from payload bytes (0–3)."""
    if not data:
        return 0
    sample = data[:256]
    unique = len(set(sample))
    ratio = unique / len(sample)
    if ratio < 0.25:
        return 0  # very low entropy, highly compressible
    if ratio < 0.5:
        return 1  # low-medium entropy
    if ratio < 0.75:
        return 2  # medium-high entropy
    return 3  # high entropy


def plan_from_header(
    header: SemanticHeader, templates: TemplateLibrary | None = None
) -> SemanticPlan:
    """Build a simple execution plan from a semantic header.

    This function does not perform any compression or GPU work; it only
    maps codec/domain/template ids to high-level choices that a caller
    can use to select CUDA/TensorRT pipelines.
    """
    codec_label = _CODEC_LABELS.get(header.codec_id, f"unknown_{header.codec_id}")

    # Default plan parameters
    model_tier = "medium"
    quantization = "fp16"
    max_seq = 2048

    if codec_label == "Sa":
        model_tier = "small"
        quantization = "int8"
        max_seq = 512
    elif codec_label in {
        "Sb",
        "Sc",
        "Sd",
        "Se",
        "Sh",
        "Si",
        "Sm",
        "Sp",
        "Sr",
        "Ss",
        "Su",
        "Sy",
        "Sj",
        "Sk",
        "Sn",
        "So",
        "St",
    }:
        model_tier = "medium"
        quantization = "fp16"
        max_seq = 2048
    elif codec_label in {"Sf", "Sg", "Sl", "Sv", "Sw", "Sx"}:
        model_tier = "large"
        quantization = "fp16"
        max_seq = 4096
    elif codec_label in {"Sq", "Sz"}:
        # Quantization/zero-copy oriented codecs; treat as large-tier with an
        # explicit 'binary' quantization hint for downstream systems.
        model_tier = "large"
        quantization = "binary"
        max_seq = 8192

    needs_template_lookup = False
    if header.template_id != 0 and templates is not None:
        needs_template_lookup = (
            templates.get(header.domain_id, header.template_id) is not None
        )

    plan = SemanticPlan(
        codec_label=codec_label,
        domain_id=header.domain_id,
        template_id=header.template_id,
        model_tier=model_tier,
        quantization=quantization,
        max_sequence_length=max_seq,
        needs_template_lookup=needs_template_lookup,
    )
    return plan


def decode_payload_to_plan(
    payload: bytes,
    templates: TemplateLibrary | None = None,
) -> tuple[SemanticHeader, SemanticPlan, bytes]:
    """Decode a semantic payload into (header, plan, core_payload).

    This helper is intended for integration code (e.g. CUDA/TensorRT
    pipelines) that wants a one-shot way to obtain both the parsed
    header and a derived :class:`SemanticPlan`, while leaving the
    underlying core payload untouched for later decompression.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_payload_to_plan() expects a bytes-like object")

    # Local import to avoid circular dependency at module import time.
    from .semantic import SemanticHeader

    header, core_payload = SemanticHeader.from_bytes(bytes(payload))
    plan = plan_from_header(header, templates=templates)
    if plan.codec_label == "Se":
        plan.entropy_bucket = _estimate_entropy_bucket(core_payload)
    return header, plan, core_payload
