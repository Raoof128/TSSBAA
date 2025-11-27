"""Denial-of-service simulation against NRF registration endpoint."""
from __future__ import annotations

import asyncio
import logging

import httpx

from core.nfs.config import NFProfile

LOGGER = logging.getLogger("dos-nrf")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


async def flood_register(
    nrf_url: str = "http://localhost:7777",
    bursts: int = 5,
    per_burst: int = 10,
) -> list[dict[str, str]]:
    """Send rapid registration attempts to test NRF throttling logic."""

    results: list[dict[str, str]] = []
    async with httpx.AsyncClient(timeout=3.0) as client:
        for burst in range(bursts):
            LOGGER.info("Starting burst %s", burst + 1)
            tasks = []
            for idx in range(per_burst):
                forged = NFProfile(
                    nf_instance_id=f"dos-{burst}-{idx}",
                    nf_type="SMF",
                    service_endpoints=["http://dos.invalid"],
                    trust_score=0.1,
                    priority=10,
                ).dict()
                tasks.append(
                    client.post(f"{nrf_url}/register", json=forged)
                )
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for response in responses:
                if isinstance(response, Exception):
                    results.append({"status": "error", "detail": str(response)})
                    continue
                results.append({"status": response.status_code, "detail": response.text})
    return results


async def main() -> None:  # pragma: no cover - manual helper
    report = await flood_register()
    LOGGER.info("DoS simulation finished %s", report)


if __name__ == "__main__":
    asyncio.run(main())
