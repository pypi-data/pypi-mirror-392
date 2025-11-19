"""Generic routing profiles for semantic compression plans.

This module defines a neutral mapping from :class:`SemanticPlan` to an
abstract :class:`RoutingProfile` that does not depend on ORCA or any
specific inference stack. It is intended for callers that want to
decide between CPU/GPU, batch sizes and precision based on the
semantic codec, sequence length and (optionally) entropy bucket.
"""

from __future__ import annotations

from dataclasses import dataclass

from .semantic_plans import SemanticPlan


@dataclass(frozen=True)
class RoutingProfile:
    """Generic execution profile derived from a SemanticPlan.

    Attributes:
        tier: Logical model tier, e.g. \"small\", \"medium\", \"large\".
        device: Preferred device class, e.g. \"cpu\" or \"gpu\".
        precision: Preferred numeric precision string such as
            \"int8\", \"fp16\" or \"fp32\".
        batch_class: Coarse batch size class (\"tiny\", \"small\",
            \"medium\", \"large\") that callers can map to concrete
            batch sizes in their own environment.
        max_batch: Suggested upper bound for batch size when using
            this profile.
    """

    tier: str
    device: str
    precision: str
    batch_class: str
    max_batch: int


class SemanticRouter:
    """Compute a generic routing profile from a SemanticPlan."""

    def select(self, plan: SemanticPlan) -> RoutingProfile:
        """Map a SemanticPlan to a neutral RoutingProfile.

        This selector is deliberately conservative and only makes
        entropy-aware adjustments when an ``entropy_bucket`` is
        present (typically for Se – Semantic Entropy – codec labels).
        """
        tier = plan.model_tier
        precision = plan.quantization

        # Base device choice from tier; small plans default to CPU
        # unless explicitly using a large tier.
        if tier == "small":
            device = "cpu"
        else:
            device = "gpu"

        # Base batch_class and max_batch from sequence length.
        if plan.max_sequence_length <= 512:
            batch_class = "large"
            max_batch = 64
        elif plan.max_sequence_length <= 2048:
            batch_class = "medium"
            max_batch = 32
        else:
            batch_class = "small"
            max_batch = 8

        # Entropy-aware tuning: only adjust when we have a bucket.
        if plan.entropy_bucket is not None:
            bucket = plan.entropy_bucket

            # Very low / low entropy (0–1): cheap to compress, likely
            # structured. Allow larger batches and favour smaller
            # tiers when possible for energy efficiency.
            if bucket <= 1:
                if tier == "medium":
                    tier = "small"
                    if device == "gpu":
                        device = "cpu"
                if batch_class == "medium":
                    batch_class = "large"
                    max_batch = max(max_batch, 64)

            # High entropy (3): expensive to compress and less likely
            # to benefit from batching; reduce suggested batch.
            elif bucket >= 3:
                if batch_class == "large":
                    batch_class = "medium"
                    max_batch = min(max_batch, 32)
                elif batch_class == "medium":
                    batch_class = "small"
                    max_batch = min(max_batch, 16)

        return RoutingProfile(
            tier=tier,
            device=device,
            precision=precision,
            batch_class=batch_class,
            max_batch=max_batch,
        )

