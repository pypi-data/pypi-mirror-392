"""Binary interplay profiles for semantic codecs.

This module encodes how each semantic codec letter (Sa..Sz) interacts
with higher-level concerns such as entropy, yield, routing, memory, and
accelerators, using a compact bitmask. The goal is to keep the on-wire
header small (one codec_id) while allowing fast lookup of the combined
behaviour at runtime.
"""

from __future__ import annotations

from enum import IntFlag

from .semantic_plans import SemanticPlan


class InterplayFlag(IntFlag):
    """Bit flags describing cross-cutting semantic behaviour."""

    NONE = 0
    USES_ENTROPY = 1 << 0   # influenced by Se / entropy_bucket
    USES_YIELD = 1 << 1     # influenced by Sy / priority
    USES_RESOLVER = 1 << 2  # routed by Sr / resolver profiles
    USES_MEMORY = 1 << 3    # interacts with Sm / long-lived caches
    USES_DEDUP = 1 << 4     # interacts with Su / Sh
    USES_ACCEL = 1 << 5     # has accelerator-friendly shape (Sx)
    IS_NUMERIC = 1 << 6     # numeric/tensor/vector/wave (Sq/Sv/Sw)
    IS_TEXTUAL = 1 << 7     # primarily text/JSON/logs (Sa/Sb/Sf/Sg/Sp/Ss)


_INTERPLAY_BY_LABEL: dict[str, InterplayFlag] = {
    "Sa": InterplayFlag.IS_TEXTUAL | InterplayFlag.USES_YIELD | InterplayFlag.USES_RESOLVER,
    "Sb": InterplayFlag.IS_TEXTUAL | InterplayFlag.USES_ENTROPY | InterplayFlag.USES_RESOLVER,
    "Sc": InterplayFlag.IS_TEXTUAL | InterplayFlag.USES_ENTROPY | InterplayFlag.USES_RESOLVER,
    "Sd": InterplayFlag.IS_TEXTUAL | InterplayFlag.USES_MEMORY | InterplayFlag.USES_DEDUP,
    "Se": InterplayFlag.USES_ENTROPY | InterplayFlag.USES_YIELD,
    "Sf": InterplayFlag.IS_TEXTUAL | InterplayFlag.USES_ENTROPY | InterplayFlag.USES_ACCEL,
    "Sg": InterplayFlag.IS_TEXTUAL | InterplayFlag.USES_ENTROPY | InterplayFlag.USES_ACCEL,
    "Sh": InterplayFlag.USES_DEDUP | InterplayFlag.USES_MEMORY,
    "Si": InterplayFlag.USES_MEMORY | InterplayFlag.USES_RESOLVER,
    "Sl": InterplayFlag.IS_TEXTUAL | InterplayFlag.IS_NUMERIC | InterplayFlag.USES_ACCEL,
    "Sm": InterplayFlag.USES_MEMORY | InterplayFlag.USES_DEDUP,
    "Sp": InterplayFlag.IS_TEXTUAL | InterplayFlag.USES_ENTROPY,
    "Sq": InterplayFlag.IS_NUMERIC | InterplayFlag.USES_ACCEL,
    "Sr": InterplayFlag.USES_RESOLVER | InterplayFlag.USES_YIELD,
    "Ss": InterplayFlag.IS_TEXTUAL | InterplayFlag.USES_ENTROPY,
    "Su": InterplayFlag.USES_DEDUP | InterplayFlag.USES_MEMORY,
    "Sv": InterplayFlag.IS_NUMERIC | InterplayFlag.USES_ACCEL,
    "Sw": InterplayFlag.IS_NUMERIC | InterplayFlag.USES_ACCEL,
    "Sx": InterplayFlag.USES_ACCEL | InterplayFlag.USES_YIELD | InterplayFlag.USES_RESOLVER,
    "Sy": InterplayFlag.USES_YIELD,
    "Sz": InterplayFlag.IS_NUMERIC | InterplayFlag.USES_ACCEL,
    "St": InterplayFlag.IS_TEXTUAL
    | InterplayFlag.IS_NUMERIC
    | InterplayFlag.USES_ENTROPY
    | InterplayFlag.USES_MEMORY
    | InterplayFlag.USES_DEDUP
    | InterplayFlag.USES_RESOLVER,
    # Design-only letters (not yet wired in core codecs) can still
    # have interplay definitions for planning and documentation.
    "Sj": InterplayFlag.IS_TEXTUAL | InterplayFlag.IS_NUMERIC | InterplayFlag.USES_RESOLVER,
    "Sk": InterplayFlag.USES_RESOLVER,
    "Sn": InterplayFlag.USES_RESOLVER,
    "So": InterplayFlag.USES_RESOLVER | InterplayFlag.USES_YIELD,
}


def get_interplay(plan: SemanticPlan) -> InterplayFlag:
    """Return the interplay bitmask for a given SemanticPlan.

    This helper allows callers to derive cross-cutting behaviour from
    a single codec label without adding extra fields to the on-wire
    header. Unknown labels return :data:`InterplayFlag.NONE`.
    """
    return _INTERPLAY_BY_LABEL.get(plan.codec_label, InterplayFlag.NONE)
