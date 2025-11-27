import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from core.nfs.config import NFProfile, NRFSettings
from core.nfs.nrf_service import build_nrf_app
from core.nfs.security import build_attestation_token
from defence.slice_guard import SlicePolicy, slice_guard
from monitoring.slice_analyzer import detect_cross_slice_use, slice_summary


@pytest.mark.asyncio
async def test_rate_limiter_blocks_bursts():
    settings = NRFSettings(jwt_secret="secret", rate_limit_per_minute=1)
    app = build_nrf_app(settings)
    token = build_attestation_token("nf-1", "AMF", secret="secret")
    profile = NFProfile(
        nf_instance_id="nf-1",
        nf_type="AMF",
        service_endpoints=["http://nf:1"],
        priority=1,
        trust_score=1.0,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post(
            "/register",
            json=profile.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert first.status_code == 200

        second = await client.post(
            "/register",
            json=profile.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert second.status_code == 429


@pytest.mark.asyncio
async def test_slice_guard_policy():
    policy = SlicePolicy({"SMF": {"001-data"}})
    guard = slice_guard(policy)

    with pytest.raises(HTTPException):
        await guard(requested_slice="001-rogue", nf_type="SMF")


def test_slice_analyzer_detects_misuse():
    registry = [
        NFProfile(
            nf_instance_id="pcf-1",
            nf_type="PCF",
            service_endpoints=["http://pcf:1"],
            priority=1,
            trust_score=0.9,
            slices=["001-data", "001-rogue"],
        )
    ]
    offenders = detect_cross_slice_use(registry, {"PCF": ["001-data"]})
    summary = slice_summary(registry)

    assert "pcf-1" in offenders
    assert summary["001-data"] == 1
