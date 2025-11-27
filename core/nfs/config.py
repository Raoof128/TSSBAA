"""Configuration utilities for NF simulations."""
from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field, HttpUrl, IPvAnyAddress, field_validator


class NFProfile(BaseModel):
    """Represents a simulated NF profile used during registration."""

    nf_instance_id: str = Field(..., description="Unique NF instance identifier")
    nf_type: str = Field(..., description="Type of NF (AMF, SMF, etc.)")
    service_endpoints: list[HttpUrl] = Field(..., description="List of service URLs exposed by NF")
    priority: int = Field(5, description="Lower is higher priority")
    trust_score: float = Field(1.0, description="Attested trust level between 0-1")
    slices: list[str] = Field(default_factory=list, description="Slices the NF claims to serve")

    @field_validator("nf_instance_id")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        if not value:
            raise ValueError("NF identifier must not be empty")
        if " " in value:
            raise ValueError("NF identifier must not contain whitespace")
        return value


@dataclass(slots=True)
class NRFSettings:
    """Settings for the simulated NRF."""

    jwt_secret: str = "change-me"  # used for demo tokens only
    allowed_nf_types: list[str] = field(
        default_factory=lambda: ["AMF", "SMF", "NRF", "AUSF", "UDM", "UPF", "PCF", "NSSF"]
    )
    rate_limit_per_minute: int = 60
    enforce_mtls: bool = False


@dataclass(slots=True)
class NFSettings:
    """Settings for an NF client."""

    nf_type: str
    nf_instance_id: str
    nrf_url: str
    exposed_host: IPvAnyAddress | str
    exposed_port: int
    jwt_secret: str
    tls_enabled: bool = False
    slices: list[str] = field(default_factory=lambda: ["001-data"])

    def service_url(self) -> str:
        """Construct the URL the NF exposes to other NFs."""
        scheme = "https" if self.tls_enabled else "http"
        return f"{scheme}://{self.exposed_host}:{self.exposed_port}"


class RegistrationResponse(BaseModel):
    """Payload returned by the NRF after registration."""

    status: str
    nf_instance_id: str
    registry_size: int
    security_actions: dict[str, str] = Field(default_factory=dict)
