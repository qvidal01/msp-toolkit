# Getting Started with MSP Toolkit

This guide will help you get MSP Toolkit up and running quickly.

## Installation

### Option 1: Using Poetry (Recommended)

```bash
git clone https://github.com/qvidal01/msp-toolkit.git
cd msp-toolkit
poetry install
poetry shell
```

### Option 2: Using pip

```bash
git clone https://github.com/qvidal01/msp-toolkit.git
cd msp-toolkit
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

## Configuration

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** with your credentials:
   ```bash
   # Required
   RMM_API_KEY=your_api_key_here

   # Optional
   DB_HOST=localhost
   ```

3. **Create configuration file**:
   ```bash
   mkdir -p config
   cat > config/msp-toolkit.yaml <<EOF
   general:
     company_name: "Your MSP Name"
     log_level: "INFO"

   database:
     type: "sqlite"
     path: "data/msp-toolkit.db"

   health_checks:
     thresholds:
       cpu_percent: 85
       memory_percent: 90
       disk_percent: 85
   EOF
   ```

## Verify Installation

```bash
msp-toolkit --version
msp-toolkit doctor
```

## First Steps

### 1. Add Your First Client

```bash
msp-toolkit client add --name "Acme Corp" --tier premium --email admin@acme.com
```

### 2. Run Health Checks

```bash
msp-toolkit health check acme-corp
```

### 3. Generate a Report

```bash
msp-toolkit report generate acme-corp --template monthly-summary
```

## Programmatic Usage

```python
from msp_toolkit import MSPToolkit

# Initialize
toolkit = MSPToolkit.from_config("config/msp-toolkit.yaml")

# Get client manager
client_mgr = toolkit.get_client_manager()

# Create client
client = client_mgr.create("acme-corp", name="Acme Corp")

# Run health checks
health_monitor = toolkit.get_health_monitor()
results = health_monitor.run_checks("acme-corp")
```

## Next Steps

- Review [ANALYSIS_SUMMARY.md](../ANALYSIS_SUMMARY.md) for architecture
- Try [examples](../examples/) for complete workflows
- Set up [MCP server](../mcp_server/README.md) for AI integration
- Read [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute

## Troubleshooting

### Command not found: msp-toolkit

Make sure you've installed the package and activated the virtual environment:
```bash
poetry shell  # or: source venv/bin/activate
```

### Configuration errors

Verify your config file:
```bash
msp-toolkit doctor
```

### Need Help?

- Check [GitHub Issues](https://github.com/qvidal01/msp-toolkit/issues)
- Join [Discussions](https://github.com/qvidal01/msp-toolkit/discussions)
- Email: support@aiqso.io
