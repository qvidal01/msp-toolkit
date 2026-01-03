# MSP Toolkit Architecture

## Overview

MSP Toolkit is a Python package that exposes automation workflows for managed service providers via a Click-based CLI and an MCP server. The codebase is organized around a small core with utilities and an integration layer that can be expanded with adapter implementations.

- **Entry points**
  - CLI: `src/msp_toolkit/cli.py` (installed as `msp-toolkit`)
  - MCP server: `mcp_server/server.py` (also reachable via `msp-toolkit mcp`)
- **Core components**
  - `MSPToolkit` (`core/toolkit.py`): orchestrates managers and validates configuration
  - `ClientManager` (`core/client_manager.py`): client lifecycle and onboarding workflows
  - `HealthMonitor` (`core/health_monitor.py`): health checks, history, and summaries
  - `ReportGenerator` (`core/report_generator.py`): template-driven reporting
  - Models and enums (`core/models.py`) shared across modules
- **Utilities**
  - Configuration management and schema validation (`utils/config.py`)
  - Structured logging with sanitization (`utils/logger.py`)
  - Credential handling using environment variables and keyring (`utils/security.py`)
- **Storage**
  - SQLite persistence via SQLAlchemy (`storage/db.py`, `storage/models.py`)
  - Health check history, clients, and devices stored for reporting/stateful operations
- **Integrations**
  - RMM adapter contract (`integrations/rmm/base.py`) for platform-specific implementations
  - Local RMM adapter for development (`integrations/rmm/local.py`) backed by the SQLite database
- **CLI/MCP tooling**
  - Device CRUD exposed via CLI (`device` commands) and MCP (`device_list`, `device_add`)

## Data Flow

- **Configuration**
  - Loaded via `Config.from_file` or `Config.from_dict`, validated against `ConfigSchema`, and cached inside `MSPToolkit`.
  - Environment variables override file values for secure deployment.

- **CLI**
  - Global options establish config path and logging.
  - Commands resolve toolkit dependencies (`ClientManager`, `HealthMonitor`, `ReportGenerator`) on demand.
  - Errors bubble up as `MSPToolkitError` derivatives for consistent messaging.

- **Health Checks**
  - `HealthMonitor.run_checks` normalizes requested check types (strings or enums), executes simulated checks with thresholds from config, records history, and exposes summaries for reporting.
  - CPU/memory/disk checks use real host metrics via psutil; services checks are backed by the local RMM adapter/device inventory.

- **MCP Server**
  - `MCPServer` registers tool handlers from `mcp_server/tools.py`.
  - `run_server` bootstraps logging, loads configuration, and runs the stdio server for MCP-compatible clients.

## Extension Points

- Implement new RMM/backup/PSA adapters by subclassing `RMMAdapter` (and future adapter bases) and wiring them into `MSPToolkit`.
- Add new MCP tools by expanding `TOOL_SCHEMAS` and handlers in `mcp_server/tools.py` and registering them in `MCPServer._register_handlers`.
- Add report templates under `templates/reports` (Jinja2 HTML) or provide a custom `reporting.template_dir` in configuration.

## Error Handling & Logging

- All domain errors derive from `MSPToolkitError` for consistent CLI/MCP reporting.
- Logging uses structlog with masking of sensitive fields; log level is controlled via config, CLI options, or environment (`MCP_LOG_LEVEL` for the MCP server).
