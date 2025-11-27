# API Reference

This repository exposes FastAPI-based simulation endpoints. They are intentionally scoped for
in-lab experimentation only.

## NRF
- `POST /register`
  - Body: `NFProfile` (`nf_instance_id`, `nf_type`, `service_endpoints`, `priority`, `trust_score`, `slices`)
  - Headers: `Authorization: Bearer <jwt>`
  - Responses:
    - `200`: registration accepted with `RegistrationResponse`
    - `401/403`: attestation or policy failure
    - `429`: rate limit exceeded
- `GET /registry`
  - Returns list of `NFProfile` objects.
- `GET /health`
  - Liveness check.

## NF base (AMF/SMF/PCF examples)
- `GET /health`
- `GET /service`
- `POST /mock-action`
- `POST /slice/access`
  - Dependencies: JWT attestation, slice guard, schema validation
  - Body: `{ "requested_slice": "001-data", "ue_id": "lab-ue" }`
  - Headers: `Authorization`, `X-Slice-ID`, `X-NF-Type`
- `POST /policy/override`
  - Dependencies: JWT attestation, schema validation
  - Body: `{ "ue_id": "ue-id", "requested_qos": "gold" }`

## Attack scripts
All attack scripts are safe simulations executed against the local lab network:
- `attacks/nf_impersonation.py` — rogue NF registration attempt.
- `attacks/api_fuzzer.py` — mutates payloads against NRF endpoints.
- `attacks/rogue_slice.py` — unauthorized slice access simulation.
- `attacks/policy_abuse.py` — attempts to modify QoS policy.
- `attacks/dos_nrf.py` — rate-limit stress test against NRF.

## Defence helpers
- `defence/mtls_jwt_enforcer.py`: FastAPI dependency enforcing JWT + simulated mTLS header.
- `defence/api_schema_validator.py`: Schema validation dependency for request bodies.
- `defence/slice_guard.py`: Slice policy enforcement dependency.
