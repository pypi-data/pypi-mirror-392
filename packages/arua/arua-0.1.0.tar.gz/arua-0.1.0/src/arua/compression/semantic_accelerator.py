"""Prototype accelerator selector for semantic payloads (Sx).

This module sketches how accelerator selection might work for AURA-S.
It does not alter the core codecs; instead, it consumes
(:class:`SemanticPlan`) objects and produces a simple
(:class:`AcceleratorSelection`) describing which hardware lane to use.
"""

from __future__ import annotations

from dataclasses import dataclass

from .semantic_plans import SemanticPlan


@dataclass(frozen=True)
class AcceleratorSelection:
    """Chosen accelerator lane for a semantic payload."""

    backend: str  # e.g. "cpu", "gpu", "dpu"
    profile: str  # logical profile or engine name
    offload: bool  # whether to offload from CPU at all


class SemanticAcceleratorSelector:
    """Prototype selector from SemanticPlan to AcceleratorSelection."""

    def select(
        self,
        plan: SemanticPlan,
        priority: str | None = None,
    ) -> AcceleratorSelection:
        """Pick a simple accelerator lane based on the plan and priority.

        Args:
            plan: :class:`SemanticPlan` describing codec, tier, quantization, etc.
            priority: Optional hint such as ``"low"``, ``"normal"``, or ``"high"``.
        """
        # Default assumptions: medium tier -> gpu is optional; small tier -> cpu;
        # large tier or numeric/vector codecs -> gpu-friendly.
        label = plan.codec_label

        # Choose backend
        if label in {"Sq", "Sv", "Sw"}:
            backend = "gpu"
        elif label in {"Sf", "Sg"}:
            backend = "gpu"
        elif label == "Sa":
            backend = "cpu"
        else:
            backend = "cpu"

        # Decide whether we actually offload based on priority.
        offload = backend != "cpu"
        if priority == "low":
            # Low-priority traffic can stay on CPU unless it is clearly GPU-shaped.
            if label not in {"Sq", "Sv", "Sw"}:
                offload = False
        elif priority == "high":
            # High-priority traffic prefers offload when possible.
            if backend == "cpu" and label in {"Sf", "Sg"}:
                backend = "gpu"
                offload = True

        # Profile naming is deliberately generic for now.
        if backend == "gpu":
            profile = f"gpu-{plan.model_tier}-{plan.quantization}"
        else:
            profile = f"cpu-{plan.model_tier}"

        return AcceleratorSelection(backend=backend, profile=profile, offload=offload)

