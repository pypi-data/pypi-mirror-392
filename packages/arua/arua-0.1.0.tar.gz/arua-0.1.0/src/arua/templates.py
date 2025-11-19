"""Lightweight template library for domain-aware lookups.

This module provides a minimal, dependency-free abstraction for
domain-specific templates keyed by small integer IDs. It is designed
to align with the semantic header layout (domain_id + template_id)
without depending on the external AURA template system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Template:
    """In-memory template record used by ARUA."""

    domain_id: int
    template_id: int
    pattern: str
    metadata: dict[str, Any] = field(default_factory=dict)


class TemplateLibrary:
    """Simple domain-aware template registry.

    Templates are keyed by ``(domain_id, template_id)`` to support
    domain-specific binary libraries in the semantic header.
    """

    def __init__(self) -> None:
        self._templates: dict[tuple[int, int], Template] = {}

    def add(
        self,
        domain_id: int,
        template_id: int,
        pattern: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register or replace a template."""
        key = (int(domain_id), int(template_id))
        self._templates[key] = Template(
            domain_id=key[0],
            template_id=key[1],
            pattern=pattern,
            metadata=dict(metadata or {}),
        )

    def get(self, domain_id: int, template_id: int) -> Template | None:
        """Retrieve a template record, or None if not found."""
        return self._templates.get((int(domain_id), int(template_id)))

    def remove(self, domain_id: int, template_id: int) -> None:
        """Remove a template if present."""
        self._templates.pop((int(domain_id), int(template_id)), None)
