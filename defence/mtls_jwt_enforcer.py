"""Defence middleware to enforce JWT and mTLS semantics."""
from __future__ import annotations

from collections.abc import Callable

from fastapi import Header, HTTPException, Request

from core.nfs.security import explain_validation


async def attestation_dependency(
    request: Request,
    authorization: str | None = Header(default=None, convert_underscores=False),
    jwt_secret: str | None = None,
) -> None:
    """Validate incoming request tokens within any NF service.

    Attach via FastAPI dependencies to gate NF-specific endpoints. This helper also mimics
    optional mTLS enforcement by checking for the presence of ``X-Client-Cert`` headers during
    local experimentation (no real TLS is performed in this lab).
    """

    token = authorization.replace("Bearer ", "", 1) if authorization else None
    is_valid, detail = explain_validation(token, jwt_secret or "change-me")
    client_cert = request.headers.get("X-Client-Cert")

    if not is_valid:
        raise HTTPException(status_code=401, detail=detail)
    if jwt_secret and not client_cert:
        raise HTTPException(status_code=403, detail="mTLS client certificate missing (simulated)")


def dependency_factory(secret: str) -> Callable:
    """Factory to inject attestation enforcement with pre-configured secret."""

    async def dependency_wrapper(
        request: Request,
        authorization: str | None = Header(default=None, convert_underscores=False),
    ) -> None:
        return await attestation_dependency(request, authorization, jwt_secret=secret)

    return dependency_wrapper
