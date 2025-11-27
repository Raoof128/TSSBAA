"""Generic NF service simulation with auto-registration."""
from __future__ import annotations

import logging

import httpx
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from defence.api_schema_validator import schema_guard
from defence.mtls_jwt_enforcer import dependency_factory
from defence.slice_guard import default_policy, slice_guard

from .config import NFProfile, NFSettings
from .security import build_attestation_token

LOGGER = logging.getLogger("nf-service")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


class NFService:
    """Minimal NF with REST endpoints and NRF registration."""

    def __init__(self, settings: NFSettings) -> None:
        self.settings = settings
        self.app = FastAPI(title=f"Simulated {settings.nf_type}")
        self.app.add_event_handler("startup", self.register_with_nrf)
        self._register_routes()

    def _register_routes(self) -> None:
        enforcer = dependency_factory(self.settings.jwt_secret)
        slice_policy = default_policy()

        class SliceAccessRequest(BaseModel):
            requested_slice: str
            ue_id: str

        class PolicyOverrideRequest(BaseModel):
            ue_id: str
            requested_qos: str

        @self.app.get("/health")
        async def health() -> dict[str, str]:
            return {"status": "ok", "nf_type": self.settings.nf_type}

        @self.app.get("/service")
        async def service_metadata() -> dict[str, str]:
            return {
                "nf_instance_id": self.settings.nf_instance_id,
                "nf_type": self.settings.nf_type,
                "service_url": self.settings.service_url(),
            }

        @self.app.post("/mock-action")
        async def mock_action(payload: dict[str, str]) -> dict[str, str]:
            """Simulates a state-changing NF action."""

            LOGGER.info("Received mock action payload=%s", payload)
            return {"result": "ok", "received": payload}

        @self.app.post(
            "/slice/access",
            dependencies=[enforcer, slice_guard(slice_policy), schema_guard(SliceAccessRequest)],
        )
        async def slice_access(request: SliceAccessRequest) -> dict[str, str]:
            LOGGER.info(
                "Slice access request slice=%s ue=%s", request.requested_slice, request.ue_id
            )
            return {"status": "authorized", "slice": request.requested_slice}

        @self.app.post(
            "/policy/override",
            dependencies=[enforcer, schema_guard(PolicyOverrideRequest)],
        )
        async def policy_override(request: PolicyOverrideRequest) -> dict[str, str]:
            LOGGER.info(
                "Policy override requested for ue=%s qos=%s",
                request.ue_id,
                request.requested_qos,
            )
            return {"status": "rejected", "reason": "immutable policy"}

    async def register_with_nrf(self) -> None:
        """Register the NF with the NRF using attested JWT."""

        token = build_attestation_token(
            nf_instance_id=self.settings.nf_instance_id,
            nf_type=self.settings.nf_type,
            secret=self.settings.jwt_secret,
        )

        payload = NFProfile(
            nf_instance_id=self.settings.nf_instance_id,
            nf_type=self.settings.nf_type,
            service_endpoints=[self.settings.service_url()],
            priority=5,
            trust_score=0.9,
            slices=self.settings.slices,
        ).dict()

        headers = {"Authorization": f"Bearer {token}"}
        LOGGER.info(
            "Registering %s with NRF at %s",
            self.settings.nf_instance_id,
            self.settings.nrf_url,
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{self.settings.nrf_url}/register", json=payload, headers=headers
                )
                response.raise_for_status()
                LOGGER.info("Registration response %s", response.json())
            except httpx.HTTPError as exc:  # pragma: no cover - network edge
                LOGGER.error("Registration failed: %s", exc)


def build_nf_app(settings: NFSettings) -> FastAPI:
    """Build the FastAPI application for a given NF instance."""

    return NFService(settings).app


async def start_nf(settings: NFSettings) -> None:  # pragma: no cover - runtime helper
    """Run an NF with uvicorn programmatically."""
    nf_app = build_nf_app(settings)
    config = uvicorn.Config(nf_app, host=str(settings.exposed_host), port=settings.exposed_port)
    server = uvicorn.Server(config)
    await server.serve()
