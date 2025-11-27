"""Slice-aware authorization helpers."""
from __future__ import annotations

from fastapi import Header, HTTPException


class SlicePolicy:
    """Represents allowed slices per consumer NF."""

    def __init__(self, allowed: dict[str, set[str]]) -> None:
        self.allowed = allowed

    def is_allowed(self, nf_type: str, slice_id: str) -> bool:
        return slice_id in self.allowed.get(nf_type, set())


def slice_guard(policy: SlicePolicy):
    """FastAPI dependency enforcing slice membership."""

    async def dependency(
        requested_slice: str = Header(..., alias="X-Slice-ID"),
        nf_type: str = Header(..., alias="X-NF-Type"),
    ) -> None:
        if not policy.is_allowed(nf_type, requested_slice):
            raise HTTPException(status_code=403, detail="Slice access denied")

    return dependency


def default_policy() -> SlicePolicy:
    """Return a conservative baseline slice policy used by lab services."""

    return SlicePolicy(
        {
            "AMF": {"001-voice", "001-data"},
            "SMF": {"001-data"},
            "PCF": {"001-voice", "001-data", "001-iot"},
        }
    )
