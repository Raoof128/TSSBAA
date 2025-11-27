"""Slice-aware anomaly detection utilities."""
from __future__ import annotations

from collections.abc import Iterable

from core.nfs.config import NFProfile


def detect_cross_slice_use(
    registry: Iterable[NFProfile], allowed_slices: dict[str, list[str]]
) -> list[str]:
    """Identify NFs advertising endpoints for slices they are not allowed to serve."""

    offenders: list[str] = []
    for nf in registry:
        declared = getattr(nf, "slices", [])
        permitted = allowed_slices.get(nf.nf_type, [])
        if any(slice_id not in permitted for slice_id in declared):
            offenders.append(nf.nf_instance_id)
    return offenders


def slice_summary(registry: Iterable[NFProfile]) -> dict[str, int]:
    """Summarise how many NFs claim to serve each slice."""

    summary: dict[str, int] = {}
    for nf in registry:
        declared = getattr(nf, "slices", [])
        for slice_id in declared:
            summary[slice_id] = summary.get(slice_id, 0) + 1
    return summary
