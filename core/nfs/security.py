"""Security helpers for JWT-based NF attestation."""
from __future__ import annotations

import logging
import time

from jose import JWTError, jwt

ALGORITHM = "HS256"
LOGGER = logging.getLogger("nf-security")


def build_attestation_token(
    nf_instance_id: str, nf_type: str, secret: str, expires_in: int = 3600
) -> str:
    """Create a signed JWT representing an NF's attested identity.

    Parameters
    ----------
    nf_instance_id: str
        Unique NF identifier.
    nf_type: str
        Type of NF (e.g., AMF, SMF).
    secret: str
        Shared secret for signing (demo only; real deployments use mTLS/PKI).
    expires_in: int
        Token validity in seconds.
    """

    now = int(time.time())
    payload = {
        "sub": nf_instance_id,
        "nf_type": nf_type,
        "iat": now,
        "exp": now + expires_in,
        "scope": "sba.attested",
    }
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def validate_attestation_token(token: str, secret: str) -> dict[str, str]:
    """Validate a JWT token, raising descriptive errors when invalid."""

    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except JWTError as exc:  # pragma: no cover - jose already tested
        LOGGER.warning("Invalid token received: %s", exc)
        raise


def explain_validation(token: str | None, secret: str) -> tuple[bool, str]:
    """Validate a token but return structured feedback for monitoring hooks."""

    if not token:
        return False, "Missing attestation token"
    try:
        validate_attestation_token(token, secret)
    except Exception as exc:  # pragma: no cover - logging only
        return False, f"Invalid token: {exc}"
    return True, "Token valid"
