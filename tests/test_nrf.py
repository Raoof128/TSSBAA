import pytest
from httpx import ASGITransport, AsyncClient

from core.nfs.config import NFProfile, NRFSettings
from core.nfs.nrf_service import build_nrf_app
from core.nfs.security import build_attestation_token
from monitoring.nf_event_detector import (
    detect_duplicate_endpoints,
    detect_low_trust,
    summarize_registry,
)


@pytest.mark.asyncio
async def test_nrf_registration_success():
    settings = NRFSettings(jwt_secret="secret")
    app = build_nrf_app(settings)
    token = build_attestation_token("amf-1", "AMF", secret="secret")

    profile = NFProfile(
        nf_instance_id="amf-1",
        nf_type="AMF",
        service_endpoints=["http://amf:7778"],
        trust_score=0.9,
        priority=5,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/register",
            json=profile.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "registered"

        registry = await app.state.registry.list_registry()
        assert registry[0].nf_instance_id == "amf-1"


@pytest.mark.asyncio
async def test_nrf_registration_rejects_invalid_token():
    settings = NRFSettings(jwt_secret="secret")
    app = build_nrf_app(settings)
    profile = NFProfile(
        nf_instance_id="rogue",
        nf_type="SMF",
        service_endpoints=["http://rogue:1"],
        trust_score=0.1,
        priority=1,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/register", json=profile.model_dump(mode="json"))
        assert response.status_code == 401
        assert "Attestation failed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_monitoring_detectors():
    registry = [
        NFProfile(
            nf_instance_id="amf-1",
            nf_type="AMF",
            service_endpoints=["http://amf:7778"],
            trust_score=0.9,
            priority=5,
        ),
        NFProfile(
            nf_instance_id="rogue",
            nf_type="SMF",
            service_endpoints=["http://amf:7778"],
            trust_score=0.1,
            priority=1,
        ),
    ]

    low_trust = detect_low_trust(registry, threshold=0.5)
    duplicates = detect_duplicate_endpoints(registry)
    summary = summarize_registry(registry)

    assert "rogue" in low_trust
    assert "rogue" in duplicates
    assert summary["AMF"] == 1
    assert summary["SMF"] == 1
