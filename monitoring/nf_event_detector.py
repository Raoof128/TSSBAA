"""Simple monitoring utilities for detecting anomalous NF registrations."""
from __future__ import annotations

from collections.abc import Iterable

from core.nfs.config import NFProfile


def detect_low_trust(registry: Iterable[NFProfile], threshold: float = 0.5) -> list[str]:
    """Identify NF instances whose trust score is below threshold."""

    return [nf.nf_instance_id for nf in registry if nf.trust_score < threshold]


def detect_duplicate_endpoints(registry: Iterable[NFProfile]) -> list[str]:
    """Return NF IDs that advertise duplicate service endpoints (possible impersonation)."""

    seen = set()
    duplicates: list[str] = []
    for nf in registry:
        for endpoint in nf.service_endpoints:
            if endpoint in seen:
                duplicates.append(nf.nf_instance_id)
            seen.add(endpoint)
    return duplicates


def summarize_registry(registry: Iterable[NFProfile]) -> dict[str, int]:
    """Summarize registry composition by NF type."""

    summary: dict[str, int] = {}
    for nf in registry:
        summary[nf.nf_type] = summary.get(nf.nf_type, 0) + 1
    return summary
