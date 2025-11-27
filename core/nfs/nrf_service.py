"""Simulated NRF implementing registry logic and basic defence hooks.

The service validates JWT-based NF attestations, applies allow-lists, and offers a
lightweight rate limiter to prevent noisy or malicious registration loops inside the lab.
"""
from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict, deque

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from .config import NFProfile, NRFSettings, RegistrationResponse
from .security import explain_validation

LOGGER = logging.getLogger("nrf-service")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")


class NRFRegistry:
    """In-memory registry with minimal rate-limiting and auditing."""

    def __init__(self, settings: NRFSettings) -> None:
        self.settings = settings
        self.registry: dict[str, NFProfile] = {}
        self.registration_counters: dict[str, deque[float]] = defaultdict(deque)
        self.lock = asyncio.Lock()

    async def register(self, profile: NFProfile, token: str | None) -> RegistrationResponse:
        is_allowed, reason = explain_validation(token, self.settings.jwt_secret)
        if not is_allowed:
            raise HTTPException(status_code=401, detail=f"Attestation failed: {reason}")

        if profile.nf_type not in self.settings.allowed_nf_types:
            raise HTTPException(status_code=403, detail="NF type not permitted")

        async with self.lock:
            self._enforce_rate_limit(profile.nf_instance_id)

            self.registry[profile.nf_instance_id] = profile
            LOGGER.info(
                "Registered %s (%s) services=%s trust=%.2f",
                profile.nf_instance_id,
                profile.nf_type,
                profile.service_endpoints,
                profile.trust_score,
            )
            return RegistrationResponse(
                status="registered",
                nf_instance_id=profile.nf_instance_id,
                registry_size=len(self.registry),
                security_actions={"token": "validated", "mtls": str(self.settings.enforce_mtls)},
            )

    async def list_registry(self) -> list[NFProfile]:
        async with self.lock:
            return list(self.registry.values())

    def _enforce_rate_limit(self, nf_instance_id: str) -> None:
        """Simple per-NF sliding window rate limiter."""

        now = time.time()
        window_start = now - 60
        history = self.registration_counters[nf_instance_id]

        while history and history[0] < window_start:
            history.popleft()

        history.append(now)
        if len(history) > self.settings.rate_limit_per_minute:
            LOGGER.warning("Rate limit exceeded for %s", nf_instance_id)
            raise HTTPException(status_code=429, detail="Registration rate limit exceeded")


async def get_registry(request: Request) -> NRFRegistry:
    registry: NRFRegistry | None = request.app.state.registry
    if registry is None:  # pragma: no cover - startup sets this
        raise RuntimeError("Registry not initialised")
    return registry


def build_nrf_app(settings: NRFSettings) -> FastAPI:
    """Create a FastAPI app exposing NRF APIs."""

    app = FastAPI(title="Simulated NRF", version="0.1.0")
    app.state.registry = NRFRegistry(settings)

    @app.post("/register", response_model=RegistrationResponse)
    async def register_nf(
        profile: NFProfile,
        authorization: str | None = Header(default=None, convert_underscores=False),
        registry: NRFRegistry = Depends(get_registry),  # noqa: B008 - FastAPI dependency injection
    ) -> RegistrationResponse:
        token = authorization.replace("Bearer ", "", 1) if authorization else None
        return await registry.register(profile, token)

    @app.get("/registry", response_model=list[NFProfile])
    async def list_registered(
        registry: NRFRegistry = Depends(get_registry),  # noqa: B008 - FastAPI dependency injection
    ) -> list[NFProfile]:
        return await registry.list_registry()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:  # pragma: no cover - FastAPI handles
        LOGGER.warning("%s", exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app
