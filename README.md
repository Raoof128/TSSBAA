# 5G SBA Attack & Defence Lab (Simulation)

A production-grade, safe, and fully simulated 5G Service-Based Architecture (SBA) security lab.
The project models 5G Core Network Functions (NFs), attack flows, and defensive controls without
interacting with real carrier networks. Everything runs inside containers or localhost processes.

## Contents
- **Core simulation**: NRF registry plus AMF/SMF/AUSF/UDM/PCF/UPF/NSSF mock services
- **Attacks**: NF impersonation, API fuzzing, slice abuse, policy abuse, and DoS stress tests (all simulated)
- **Defences**: JWT attestation, mTLS simulation toggle, slice policy guard, schema checks, rate limiting
- **Monitoring**: Registry anomaly detection, slice analytics, JSONL sniffer/visualizer
- **Dashboard**: Static topology and alert viewer
- **Docs**: Architecture, threat model, operating guide

## Safety Notice
- The lab is self-contained and never touches real radio or carrier infrastructure.
- All "attacks" are simulations against in-lab services only.
- Do not load real credentials, RF settings, or connect to live networks.

## Quick start
```bash
# install dependencies
pip install .[dev]

# run NRF
python -m core.nfs.main nrf --host 0.0.0.0 --port 7777 --jwt-secret lab-secret

# in another shell, run sample AMF
python -m core.nfs.main nf --nf-type AMF --instance amf-1 --port 7778 --nrf-url http://localhost:7777 --jwt-secret lab-secret

# simulate a rogue NF registration attempt
python attacks/nf_impersonation.py
# exercise slice/policy protections
python attacks/rogue_slice.py
python attacks/policy_abuse.py
```

For detailed runbooks, monitoring examples, and cleanup steps see [docs/operations.md](docs/operations.md).

### Makefile shortcuts
```bash
make install   # install dependencies
make check     # lint + tests + formatting check
make docker-up # launch compose sandbox
make docker-down
```

### Dev containers
A [VS Code devcontainer](.devcontainer/devcontainer.json) is provided for a preconfigured Python 3.11
environment with Ruff and Pylance. Open the repository in VS Code and choose **Reopen in Container**.

## Docker Compose lab
A multi-service sandbox is available via Docker Compose.
```bash
cd core
docker compose up --build
```
Services:
- `nrf` on `7777`
- `amf` on `7778`
- `smf` on `7779`
- `pcf` on `7781`
- `rogue-smf` executes the impersonation attack script

## Architecture
```mermaid
graph TD
  subgraph ControlPlane[Control Plane (Simulated)]
    NRF((NRF))
    AMF((AMF))
    SMF((SMF))
    AUSF((AUSF))
    UDM((UDM))
    PCF((PCF))
    NSSF((NSSF))
  end
  subgraph Defence[Defence + Monitoring]
    IDS[Monitoring detectors]
    ENF[JWT / mTLS enforcer]
  end
  AMF -->|Namf| NRF
  SMF -->|Nsmf| NRF
  AUSF -->|Nausf| NRF
  UDM -->|Nudm| NRF
  PCF -->|Npcf| NRF
  NSSF -->|Nnssf| NRF
  IDS --> NRF
  ENF --> NRF
```

### Key components
- **NRF** (`core/nfs/nrf_service.py`): Registry with JWT validation, allow-list enforcement, and rate limiting.
- **NF base** (`core/nfs/nf_service.py`): Auto-registers with NRF using signed JWTs and exposes mock endpoints.
- **Security helpers** (`core/nfs/security.py`): Token issuance/validation for attestation.
- **Attack** (`attacks/`): Rogue NF registration, fuzzing, slice abuse, policy abuse, and DoS simulations.
- **Defence** (`defence/mtls_jwt_enforcer.py`): FastAPI dependency for JWT + mTLS (simulated) enforcement.
- **Defence** (`defence/api_schema_validator.py`): Request validation dependency to reject malformed inputs.
- **Defence** (`defence/slice_guard.py`): Slice allow-list enforcement helper.
- **Monitoring** (`monitoring/nf_event_detector.py`): Detect low-trust NFs, duplicate endpoints, and summarize registry.
- **Monitoring** (`monitoring/slice_analyzer.py`): Detect cross-slice abuse and summarise slice coverage.
- **Sniffer** (`monitoring/sba_sniffer.py`): Renders JSONL capture files as alert tables.
- **Dashboard** (`dashboard/`): Static visualiser showing NF graph, alerts, and posture.

## Operating the lab
1. Start the NRF.
2. Launch NF processes (AMF, SMF, etc.) with the shared `--jwt-secret`.
3. Run attack scripts to observe detection and registry state.
4. Use monitoring utilities to inspect registry anomalies.
5. Open `dashboard/index.html` for a quick topology view (static demo data by default).
6. Review [docs/api.md](docs/api.md) and [docs/lab_manual.md](docs/lab_manual.md) for deeper guidance.
7. Contributor tooling and workflows are documented in [docs/development.md](docs/development.md).

### Example: programmatic registration
```python
from core.nfs.config import NFSettings
from core.nfs.nf_service import build_nf_app
import uvicorn

settings = NFSettings(
    nf_type="PCF",
    nf_instance_id="pcf-1",
    nrf_url="http://localhost:7777",
    exposed_host="0.0.0.0",
    exposed_port=7780,
    jwt_secret="lab-secret",
)
uvicorn.run(build_nf_app(settings), host=settings.exposed_host, port=settings.exposed_port)
```

## Testing and linting
```bash
pytest
ruff check .
```

## Project structure
```
.devcontainer/devcontainer.json # VS Code dev container
.github/workflows/ci.yml        # Lint + test automation
Makefile                        # Developer shortcuts
attacks/                       # Safe attack simulations
  api_fuzzer.py
  dos_nrf.py
  nf_impersonation.py
  policy_abuse.py
  rogue_slice.py
core/
  Dockerfile                   # Base image for NF/NRF containers
  docker-compose.yml           # Multi-service lab stack
  nfs/
    config.py
    main.py
    nf_service.py
    nrf_service.py
    security.py
dashboard/
  index.html
  dashboard.js
  styles.css
defence/
  api_schema_validator.py
  mtls_jwt_enforcer.py
  slice_guard.py
docs/
  api.md
  architecture.md
  lab_manual.md
  operations.md
  development.md
  sample_captures/
    sba_events.jsonl
monitoring/
  nf_event_detector.py
  sba_sniffer.py
  slice_analyzer.py
pyproject.toml
setup.cfg
tests/
  test_defence_monitoring.py
  test_nrf.py
LICENSE
README.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
SECURITY.md
```

## Threat model
- **Attacks simulated**: NF impersonation, malformed payloads, low-trust registrations, duplicate endpoints.
- **Detections**: JWT validation failures, rate-limit hits, low trust scores, endpoint collisions.
- **Defences**: JWT/mTLS simulation, allow-listing NF types, registry audit helpers, rate limiting hooks.

## Extending the lab
- Add more attacks (e.g., API fuzzing, slice-crossing) in `attacks/`.
- Extend defence middleware with schema validation and per-slice authorization.
- Feed live capture JSONL into `monitoring/sba_sniffer.py` to render alerts.
- Wire the dashboard to backend APIs for real-time visuals.

## License
MIT. See [LICENSE](LICENSE).
