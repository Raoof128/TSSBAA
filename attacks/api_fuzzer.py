"""Safe API fuzzing simulation against SBA interfaces.

This module sends controlled, schema-aware mutations to the NRF and NF mock
endpoints to exercise validation and defensive code paths. Payloads remain
in-bounds for the lab; no real-world network calls are performed.
"""
from __future__ import annotations

import asyncio
import logging
import random

import httpx
from pydantic import BaseModel, ValidationError

LOGGER = logging.getLogger("api-fuzzer")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


class FuzzPlan(BaseModel):
    """Configuration describing which paths to fuzz and with what payloads."""

    target_base: str
    paths: list[str]
    tokens: list[str]
    sample_payloads: list[dict[str, object]]


def mutate_payload(payload: dict[str, object]) -> dict[str, object]:
    """Generate a mutated payload that remains JSON-serialisable."""

    mutation = dict(payload)
    if not mutation:
        return {"noise": random.randint(0, 1000)}  # noqa: S311 - lab-safe fuzzing

    key = random.choice(list(mutation.keys()))  # noqa: S311 - lab-safe fuzzing
    mutation[key] = [mutation[key], "fuzz"]
    return mutation


async def run_fuzz(plan: FuzzPlan) -> list[dict[str, object]]:
    """Execute fuzzing attempts against configured endpoints."""

    results: list[dict[str, object]] = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for path in plan.paths:
            for payload in plan.sample_payloads:
                mutated = mutate_payload(payload)
                token = random.choice(plan.tokens) if plan.tokens else None  # noqa: S311
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                try:
                    response = await client.post(
                        f"{plan.target_base}{path}", json=mutated, headers=headers
                    )
                    results.append({
                        "path": path,
                        "status": response.status_code,
                        "detail": response.text,
                    })
                except httpx.HTTPError as exc:  # pragma: no cover - network edge
                    LOGGER.warning("Fuzz request failed for %s: %s", path, exc)
                    results.append({"path": path, "status": "error", "detail": str(exc)})
    return results


async def main() -> None:  # pragma: no cover - manual helper
    try:
        plan = FuzzPlan(
            target_base="http://localhost:7777",
            paths=["/register"],
            tokens=[],
            sample_payloads=[{"nf_instance_id": "", "nf_type": 123}],
        )
    except ValidationError as exc:  # pragma: no cover - user feedback
        LOGGER.error("Invalid fuzz plan: %s", exc)
        return

    report = await run_fuzz(plan)
    LOGGER.info("Fuzzing complete %s", report)


if __name__ == "__main__":
    asyncio.run(main())
