# Lab Manual

## Prerequisites
- Python 3.10+
- Docker (for the compose sandbox)
- No access to real carrier networks required (and not allowed)

## Running locally
```bash
pip install .[dev]
python -m core.nfs.main nrf --host 0.0.0.0 --port 7777 --jwt-secret lab-secret
python -m core.nfs.main nf --nf-type AMF --instance amf-1 --port 7778 --nrf-url http://localhost:7777 --jwt-secret lab-secret
```

## Using Docker Compose
```bash
cd core
docker compose up --build
```

## Observing attacks
- NF impersonation: `python attacks/nf_impersonation.py`
- API fuzzing: `python attacks/api_fuzzer.py`
- DoS simulation: `python attacks/dos_nrf.py`
- Slice abuse: `python attacks/rogue_slice.py`
- Policy abuse: `python attacks/policy_abuse.py`

## Defensive controls
- JWT + mTLS toggle via `defence/mtls_jwt_enforcer.py`
- Schema validation via `defence/api_schema_validator.py`
- Slice policy enforcement via `defence/slice_guard.py`

## Monitoring
- Registry anomaly detection: `monitoring/nf_event_detector.py`
- Slice analytics: `monitoring/slice_analyzer.py`
- Alert rendering: `monitoring/sba_sniffer.py ./docs/sample_captures/sba_events.jsonl`

## Safety
- Never point endpoints to real networks.
- Use only the included JWT secrets for local demos; rotate for your own lab runs.
