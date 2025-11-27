# Contributing Guidelines

Thank you for your interest in improving the 5G SBA Attack & Defence Lab. We welcome
issues, documentation fixes, tests, and new security scenarios. Please keep the lab safe,
non-destructive, and focused on education.

## Development workflow
1. Fork the repository and create a feature branch.
2. Install dependencies with `pip install .[dev]`.
3. Run tests with `pytest` and lint with `ruff .`.
4. Document your change in the README where applicable.
5. Submit a pull request describing the motivation, design, and validation steps.

## Code standards
- Prefer Python 3.10+ type hints and docstrings for all public functions.
- Follow defensive coding practices: input validation, error handling, and logging.
- Keep simulations isolated from real networks; never include live credentials or radio settings.

## Reporting issues
Use GitHub issues with a clear reproduction, expected behavior, and environment details.
Security issues should be reported following `SECURITY.md`.
