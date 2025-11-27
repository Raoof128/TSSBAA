"""Simulate unauthorized slice access attempts."""
from __future__ import annotations

import asyncio
import logging

import httpx

LOGGER = logging.getLogger("rogue-slice")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


async def attempt_slice_access(
    pcf_url: str = "http://localhost:7781",
    slice_id: str = "001-rogue",
    auth_token: str | None = None,
) -> dict[str, str]:
    """Attempt to access a protected slice-aware endpoint."""

    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    payload = {"requested_slice": slice_id, "ue_id": "lab-ue"}
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(f"{pcf_url}/slice/access", json=payload, headers=headers)
            response.raise_for_status()
            LOGGER.warning("Unexpected slice access allowed: %s", response.json())
            return {"result": "allowed", "detail": str(response.json())}
        except httpx.HTTPStatusError as exc:
            LOGGER.info(
                "Slice access blocked status=%s detail=%s",
                exc.response.status_code,
                exc.response.text,
            )
            return {
                "result": "blocked",
                "status": str(exc.response.status_code),
                "detail": exc.response.text,
            }
        except httpx.HTTPError as exc:  # pragma: no cover - network edge
            LOGGER.error("Slice access errored: %s", exc)
            return {"result": "error", "detail": str(exc)}


if __name__ == "__main__":  # pragma: no cover - manual helper
    asyncio.run(attempt_slice_access())
