# MSP Toolkit - Claude Reference

## Quick Overview
Managed Service Provider toolkit for client management, health monitoring, automated reporting, and RMM/PSA integration.

## Tech Stack
- **Language:** Python 3.10+
- **Validation:** Pydantic
- **CLI:** Click + Rich
- **Database:** SQLAlchemy
- **HTTP:** HTTPX (async)
- **Templates:** Jinja2
- **Scheduling:** Schedule
- **AI:** MCP Server (v0.9)
- **Package:** Poetry

## Project Structure
```
src/msp_toolkit/
├── client/              # Client management
├── health/              # Health monitoring
├── reporting/           # Report generation
├── integrations/        # RMM/PSA adapters
├── mcp_server/          # MCP server for Claude
├── cli/                 # Command-line interface
├── models/              # Data models
└── utils/               # Utilities

tests/                   # Unit tests
docs/                    # Documentation
examples/                # Usage examples
```

## Quick Commands
```bash
# Install
poetry install

# Run CLI
poetry run msp-toolkit --help

# Client list
poetry run msp-toolkit client list

# Health check
poetry run msp-toolkit health check --client-id xyz

# Generate report
poetry run msp-toolkit report generate --template monthly
```

## MCP Server Tools
| Tool | Purpose |
|------|---------|
| `client_list` | List & filter clients |
| `client_onboard` | Automated onboarding |
| `health_check` | System health checks |
| `backup_verify` | Verify backup status |
| `report_generate` | Generate reports |
| `alert_list` | Active alerts |
| `device_list` | Client devices |

## Key Features
- Client lifecycle management
- Multi-platform health monitoring
- Automated reporting (templates)
- RMM integration (ConnectWise, Datto, NinjaRMM)
- Backup verification
- AI integration via MCP
- Secure credentials (Keyring)
- Extensible plugin architecture

## Planned Integrations
- **RMM:** ConnectWise, Datto, NinjaRMM
- **PSA:** ConnectWise Manage, Autotask
- **Backup:** Veeam, Acronis
- **Notifications:** Email, Slack, Teams

## Status: Alpha (v0.1)
- Core framework
- Client management
- Health monitoring
- Reporting
- MCP server

## Documentation
- `ANALYSIS_SUMMARY.md` - Architecture
- `IMPROVEMENT_PLAN.md` - Roadmap
