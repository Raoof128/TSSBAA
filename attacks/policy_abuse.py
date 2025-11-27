"""Policy manipulation simulation targeting PCF-like endpoints."""
from __future__ import annotations

import asyncio
import logging

import httpx

LOGGER = logging.getLogger("policy-abuse")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


async def manipulate_policy(
    pcf_url: str = "http://localhost:7781",
    ue_id: str = "ue-test-1",
    new_qos: str = "gold",
    token: str | None = None,
) -> dict[str, str]:
    """Attempt to override QoS settings via PCF API."""

    payload = {"ue_id": ue_id, "requested_qos": new_qos}
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(
                f"{pcf_url}/policy/override", json=payload, headers=headers
            )
            response.raise_for_status()
            LOGGER.warning("Policy override succeeded unexpectedly: %s", response.json())
            return {"result": "allowed", "detail": str(response.json())}
        except httpx.HTTPStatusError as exc:
            LOGGER.info("Policy override blocked status=%s", exc.response.status_code)
            return {
                "result": "blocked",
                "status": str(exc.response.status_code),
                "detail": exc.response.text,
            }
        except httpx.HTTPError as exc:  # pragma: no cover - network edge
            LOGGER.error("Policy override errored: %s", exc)
            return {"result": "error", "detail": str(exc)}


if __name__ == "__main__":  # pragma: no cover - manual helper
    asyncio.run(manipulate_policy())
