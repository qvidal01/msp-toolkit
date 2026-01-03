# Changelog

## Unreleased

- Added Pydantic-backed configuration schema and validation with defaults for health thresholds, logging, and reporting paths.
- `MSPToolkit` now validates configuration during initialization to catch misconfiguration early.
- Implemented functional `health check --all` CLI command and stricter tier handling in `client add`.
- Enabled MCP server startup from the CLI via `msp-toolkit mcp`, reusing shared logging configuration.
- Expanded unit test coverage for configuration validation, CLI smoke tests, health monitor check type coercion, and client tier validation.
- Introduced SQLite persistence for clients, devices, and health check history (SQLAlchemy-backed).
- Health checks now use real system metrics (psutil) and store results for reporting; services checks rely on the local RMM adapter inventory.
- Added a local RMM adapter for development plus a default health report template.
- Included psutil dependency for host metrics collection.
- Added device CRUD via CLI/MCP and local RMM-backed inventory for development.
- Health report template now includes alert/ticket sections (populated when adapters supply data).
