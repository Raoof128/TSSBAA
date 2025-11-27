.PHONY: install lint test format check docker-up docker-down docs

install:
python -m pip install --upgrade pip
pip install -e .[dev]

lint:
ruff check .

format:
ruff format .

check: lint test
ruff format --check .
ruff check .
echo "Lint and tests complete"

test:
pytest

docker-up:
cd core && docker compose up --build

docker-down:
cd core && docker compose down -v

docs:
@echo "Key docs: README.md, docs/operations.md, docs/lab_manual.md, docs/architecture.md, docs/api.md, docs/development.md"
