"""Request body validation helpers for FastAPI endpoints."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Body, HTTPException
from pydantic import BaseModel, ValidationError


def schema_guard(model: type[BaseModel]) -> Callable[[Any], Any]:
    """Return a dependency that validates request bodies against ``model``.

    This function is intentionally lightweight and should be used in conjunction with
    authentication/authorization layers to build defence-in-depth for SBA APIs.
    """

    async def validate(payload: Any = Body(...)) -> Any:  # noqa: B008 - FastAPI dependency
        try:
            model.model_validate(payload)
        except ValidationError as exc:
            raise HTTPException(status_code=400, detail=f"Schema validation failed: {exc}") from exc
        return payload

    return validate
