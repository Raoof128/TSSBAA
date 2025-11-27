# Operations & Lab Playbook

This playbook documents how to run, observe, and extend the simulated 5G SBA lab safely.
Use it alongside the README for quick start and the API reference for request shapes.

## Environment setup
- Python 3.10+
- Dependencies: `pip install .[dev]`
- Optional container stack: Docker + Docker Compose

## Running the control plane locally
1. Start the NRF service with a shared secret:
   ```bash
   python -m core.nfs.main nrf --host 0.0.0.0 --port 7777 --jwt-secret lab-secret
   ```
2. Launch one or more NF instances (example AMF and SMF):
   ```bash
   python -m core.nfs.main nf --nf-type AMF --instance amf-1 --port 7778 --nrf-url http://localhost:7777 --jwt-secret lab-secret
   python -m core.nfs.main nf --nf-type SMF --instance smf-1 --port 7779 --nrf-url http://localhost:7777 --jwt-secret lab-secret
   ```
3. Confirm health:
   ```bash
   curl -s http://localhost:7777/health
   curl -s http://localhost:7778/health
   curl -s http://localhost:7779/health
   ```

## Containerised lab
```bash
cd core
docker compose up --build
```
Services: NRF (7777), AMF (7778), SMF (7779), PCF (7781), and a rogue SMF attacker container.
Stop with `docker compose down`.

## Simulated attack flows
> All attacks stay inside the lab network and exercise validation paths.

- **NF impersonation**: `python attacks/nf_impersonation.py`
- **API fuzzing**: `python attacks/api_fuzzer.py`
- **Unauthorized slice access**: `python attacks/rogue_slice.py`
- **Policy manipulation**: `python attacks/policy_abuse.py`
- **NRF DoS stress**: `python attacks/dos_nrf.py`

Expected outcomes: 401/403/429 responses with detailed error strings; review service logs for detections.

## Defence and observability
- Enable simulated mTLS and JWT enforcement in NF routes via `defence/mtls_jwt_enforcer.py`.
- Apply schema validation and slice allow-lists with `defence/api_schema_validator.py` and `defence/slice_guard.py`.
- Inspect registry anomalies:
  ```bash
  python -m monitoring.nf_event_detector
  ```
- Analyse slice behaviour:
  ```bash
  python -m monitoring.slice_analyzer
  ```
- Render JSONL captures to HTML tables:
  ```bash
  python monitoring/sba_sniffer.py docs/sample_captures/sba_events.jsonl
  ```

## Dashboard preview
Open `dashboard/index.html` locally. The page uses static demo data but can be wired to live APIs.

## Safety and teardown
- Use only lab-provided secrets and endpoints. No real RF or carrier interaction is supported.
- Remove containers with `docker compose down -v` to delete persistent state.
- Rotate JWT secrets regularly when collaborating to keep attestation integrity intact.
