"""NF impersonation simulation against the NRF registry."""
from __future__ import annotations

import asyncio
import logging

import httpx

from core.nfs.config import NFProfile

LOGGER = logging.getLogger("nf-impersonation")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


async def impersonate(
    nrf_url: str = "http://localhost:7777",
    forged_nf_type: str = "SMF",
    forged_id: str = "rogue-smf-001",
    token: str | None = None,
) -> dict[str, str]:
    """Attempt to register a rogue NF with optional forged token."""

    payload = NFProfile(
        nf_instance_id=forged_id,
        nf_type=forged_nf_type,
        service_endpoints=["http://rogue:9999"],
        priority=1,
        trust_score=0.1,
    ).dict()

    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(
                f"{nrf_url}/register", json=payload, headers=headers
            )
            response.raise_for_status()
            LOGGER.warning(
                "Rogue NF registration unexpectedly succeeded response=%s", response.json()
            )
            return {"result": "success", "response": str(response.json())}
        except httpx.HTTPStatusError as exc:
            LOGGER.warning(
                "Rogue NF blocked with status %s detail=%s",
                exc.response.status_code,
                exc.response.text,
            )
            return {
                "result": "blocked",
                "status": str(exc.response.status_code),
                "detail": exc.response.text,
            }
        except httpx.HTTPError as exc:
            LOGGER.error("Network error during impersonation: %s", exc)
            return {"result": "error", "detail": str(exc)}


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    asyncio.run(impersonate())
