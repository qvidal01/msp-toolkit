# Installation Guide

## Prerequisites

- Python **3.10+**
- `pip` (or `poetry` if you prefer)
- `virtualenv`/`venv` for isolation

## Standard Installation (pip)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install -e .           # install in editable mode
pip install -r requirements-dev.txt  # for tests and linting
```

The toolkit defaults to SQLite storage at `data/msp-toolkit.db`. Override `database.path` in your configuration to change the location.

## Poetry Installation

```bash
curl -sSL https://install.python-poetry.org | python -  # if poetry is not installed
poetry install --with dev
poetry run msp-toolkit --version
```

## Configuration

1. Copy `.env.example` to `.env` and fill in credentials or point to a secrets manager.
2. Create `config/msp-toolkit.yaml` and populate general, database, health check, and reporting sections.
3. Validate the setup:

```bash
msp-toolkit doctor --config config/msp-toolkit.yaml
```

## Development Workflow

- Format: `black src/ tests/`
- Lint: `ruff check src/ tests/`
- Type check: `mypy src/`
- Tests: `pytest`

## Troubleshooting

- **Missing dependencies:** reinstall dev requirements (`pip install -r requirements-dev.txt` or `poetry install --with dev`).
- **Config errors:** `msp-toolkit doctor` reports schema violations; fix the referenced keys.
- **MCP server:** ensure `MSP_CONFIG` points to a valid config file; use `MCP_LOG_LEVEL=DEBUG` for troubleshooting.
- **System metrics:** psutil is required for host health checks; it is installed via requirements.
