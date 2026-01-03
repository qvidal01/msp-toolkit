# Implementation Notes

## Configuration Validation

- `utils/config.py` now defines a `ConfigSchema` powered by Pydantic.
- `MSPToolkit` calls `config.validate()` during initialization to fail fast on invalid or empty configs.
- Defaults are applied (log level, health thresholds, reporting paths) and persisted back into the in-memory config.
- Database config now defaults to SQLite at `data/msp-toolkit.db`.

## CLI Improvements

- `client add` coerces tier input to `ClientTier`, ensuring invalid tiers raise a `ValidationError`.
- `health check --all` now iterates known clients and prints per-client results instead of a placeholder.
- The MCP server can be launched via `msp-toolkit mcp`, reusing the same configuration/logging settings.

## Health Monitoring

- `HealthMonitor.run_checks` accepts both enum and string check types, normalizes them, and rejects unsupported values.
- History and summaries continue to accumulate per-client; thresholds are read from validated configuration.
- Health checks now use real system metrics (psutil) for CPU/memory/disk and persist results to SQLite. Services checks are driven by the local RMM adapter inventory.

## MCP Server

- `run_server` centralizes MCP startup with logging bootstrap, enabling reuse from the CLI entrypoint.
- Tool handlers remain in `mcp_server/tools.py`; server registration is contained in `MCPServer._register_handlers`.

## Persistence & Integrations

- Added a SQLite-backed storage layer (`storage/db.py`, `storage/models.py`) for clients, devices, and health checks.
- ClientManager and HealthMonitor now read/write through SQLAlchemy instead of in-memory dicts.
- Local RMM adapter (`integrations/rmm/local.py`) uses the same database to manage device inventory for development/testing.
- Report generation can consume persisted health summaries and check history; a default health report template lives under `templates/reports/health-report.html`.
- Added device CRUD via CLI and MCP (`device_list`, `device_add`) backed by SQLite.
- Report template includes placeholders for alerts and tickets to be fed by future adapters.

## Testing

- Added unit coverage for configuration validation, CLI smoke tests, health check type coercion, and client tier validation.
- CLI tests write a minimal config fixture to isolate behavior and avoid touching user files.
