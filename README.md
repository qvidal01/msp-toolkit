# 🛠️ MSP Toolkit

[![CI](https://github.com/qvidal01/msp-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/qvidal01/msp-toolkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**AI-Powered Automation Toolkit for Managed Service Providers**

MSP Toolkit is a comprehensive Python framework for automating common MSP tasks, featuring RMM integration, health monitoring, automated reporting, and AI-powered workflows via Model Context Protocol (MCP) integration.

---

## ✨ Features

- **🎯 Client Management**: Automated onboarding, configuration, and lifecycle management
- **🏥 Health Monitoring**: Multi-platform system health checks with threshold-based alerting
- **📊 Automated Reporting**: Professional client reports with customizable templates
- **🗄️ Persistent Inventory**: SQLite-backed client/device state out of the box
- **🔌 RMM Integration**: Unified API for ConnectWise, Datto, NinjaRMM, and more
- **💾 Backup Verification**: Automated backup status checks and compliance tracking
- **🤖 AI Integration**: MCP server for conversational automation with Claude and other AI agents
- **🔐 Security First**: Secure credential management, input validation, and audit logging
- **🧩 Extensible**: Plugin architecture for custom integrations

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip or Poetry
- Git

### Installation

#### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/qvidal01/msp-toolkit.git
cd msp-toolkit

# Install with Poetry
poetry install

# Activate virtual environment
poetry shell

# Initialize configuration
msp-toolkit init

# Verify installation
msp-toolkit --version
```

#### Using pip

```bash
# Clone the repository
git clone https://github.com/qvidal01/msp-toolkit.git
cd msp-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Initialize configuration
msp-toolkit init

# Verify installation
msp-toolkit --version
```

### Configuration

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials**:
   ```bash
   # Edit with your favorite editor
   nano .env
   ```

3. **Create configuration file**:
   ```bash
   mkdir -p config
   msp-toolkit config init > config/msp-toolkit.yaml
   ```

4. **Verify configuration**:
   ```bash
   msp-toolkit doctor
   ```
   The doctor command performs schema validation and will fail fast if required sections are missing or misconfigured.

---

## 📖 Usage Examples

### Client Management

```bash
# List all clients
msp-toolkit client list

# Add new client
msp-toolkit client add --name "Acme Corp" --tier premium

# Onboard client with automated setup
msp-toolkit client onboard acme-corp --template standard-business

# View client details
msp-toolkit client show acme-corp
```

### Health Monitoring

```bash
# Run health check for all clients
msp-toolkit health check --all

# Run check for specific client
msp-toolkit health check acme-corp

# View health history
msp-toolkit health history acme-corp --days 7
```

### Report Generation

```bash
# Generate monthly report
msp-toolkit report generate acme-corp --template monthly-summary --format pdf

# Generate reports for all clients
msp-toolkit report generate --all --month 2024-01
```

### Programmatic Usage

```python
from msp_toolkit import MSPToolkit

# Initialize toolkit
toolkit = MSPToolkit.from_config("config/msp-toolkit.yaml")

# Get client manager
client_mgr = toolkit.get_client_manager()
clients = client_mgr.list_clients(filters={"tier": "premium"})

# Run health checks
health_monitor = toolkit.get_health_monitor()
for client in clients:
    results = health_monitor.run_checks(client.id)
    print(f"{client.name}: {results.summary}")
```

---

## 🤖 AI Integration (MCP Server)

MSP Toolkit includes an MCP server for AI-powered automation. Use it with Claude Desktop or other MCP-compatible clients.

### Setup MCP Server

1. **Add to Claude Desktop config** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "msp-toolkit": {
      "command": "msp-toolkit",
      "args": ["mcp"],
      "env": {
        "MSP_CONFIG": "/path/to/config/msp-toolkit.yaml"
      }
    }
  }
}
```

2. **Restart Claude Desktop**

3. **Try it out**:
   - "List all my premium tier clients"
   - "Run health checks for Acme Corp and summarize the results"
   - "Generate a monthly report for all clients"

### Available MCP Tools

- `client_list` - List and filter clients
- `client_onboard` - Automate client onboarding
- `health_check` - Run system health checks
- `device_list` - List client devices (optionally by client)
- `device_add` - Register a device for a client
- `backup_verify` - Verify backup status
- `report_generate` - Generate client reports
- `alert_list` - Get active alerts

See [MCP Documentation](docs/mcp_integration.md) for details.

### Running the MCP Server

Launch the MCP server directly from the CLI:

```bash
msp-toolkit mcp --config config/msp-toolkit.yaml
```

Set `MCP_LOG_LEVEL=DEBUG` for verbose logging while building new workflows.

---

## 🧰 Data & Persistence

- Default storage is SQLite (`data/msp-toolkit.db`); configure via `database.path`.
- Health check history is persisted for reporting and summaries.
- A lightweight local RMM adapter uses the same database for device inventory in development environments.

---

## 📚 Documentation

- **[Getting Started Guide](docs/getting_started.md)** - Detailed installation and setup
- **[Configuration Guide](docs/configuration.md)** - All configuration options explained
- **[API Documentation](docs/api/)** - Complete API reference
- **[MCP Integration](docs/mcp_integration.md)** - AI-powered automation setup
- **[Plugin Development](docs/plugin_development.md)** - Create custom plugins
- **[Examples](examples/)** - Runnable code examples
- **[Installation Guide](INSTALL.md)** - Environment setup and tooling
- **[Architecture](ARCHITECTURE.md)** - Current code layout and extension points
- **[Implementation Notes](IMPLEMENTATION_NOTES.md)** - Recent design decisions
- **[Changelog](CHANGELOG.md)** - Release notes
- **[ANALYSIS_SUMMARY.md](ANALYSIS_SUMMARY.md)** - Deep technical analysis

---

## 🏗️ Architecture

```
MSP Toolkit
├── Core Layer (client management, health monitoring, reporting)
├── Integration Layer (RMM, backup, PSA, cloud adapters)
├── MCP Server (AI agent integration)
└── Utilities (config, logging, security, validation)
```

See [ANALYSIS_SUMMARY.md](ANALYSIS_SUMMARY.md) for detailed architecture documentation.

---

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/qvidal01/msp-toolkit.git
cd msp-toolkit

# Install with dev dependencies
poetry install --with dev

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/msp_toolkit --cov-report=html

# Lint code
ruff check src/

# Format code
black src/ tests/

# Type check
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_client_manager.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src/msp_toolkit --cov-report=term-missing
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Good First Issues

Looking for good first issues? Check out issues labeled [`good first issue`](https://github.com/qvidal01/msp-toolkit/labels/good%20first%20issue).

---

## 🛡️ Security

- Secure credential management via OS keyring or environment variables
- Input validation and sanitization on all user inputs
- Audit logging for all privileged operations
- Regular security updates and dependency scanning

**Found a security issue?** Please see [SECURITY.md](SECURITY.md) for responsible disclosure.

---

## 📋 Roadmap

### v1.0 (Current) - Foundation
- ✅ Core framework and CLI
- ✅ Client management
- ✅ Health monitoring
- ✅ Report generation
- ✅ MCP server integration
- ✅ Mock RMM adapter + ConnectWise integration

### v1.1 - Enhanced Integrations
- 🔲 Additional RMM platforms (Datto, NinjaRMM)
- 🔲 Backup integrations (Veeam, Acronis)
- 🔲 Alerting system (Email, Slack, Teams)
- 🔲 PSA integration (ConnectWise Manage, Autotask)

### v2.0 - Advanced Features
- 🔲 Web dashboard
- 🔲 ML-powered anomaly detection
- 🔲 Advanced analytics and insights
- 🔲 Mobile app

See [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) for detailed roadmap.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with ❤️ by the [AIQSO](https://aiqso.io) team
- Powered by [Model Context Protocol](https://modelcontextprotocol.io/)
- Inspired by the MSP community

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/qvidal01/msp-toolkit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/qvidal01/msp-toolkit/discussions)
- **Email**: support@aiqso.io

---

**Made with ❤️ by [AIQSO](https://aiqso.io)**

*Automate your MSP. Empower your team. Delight your clients.*
