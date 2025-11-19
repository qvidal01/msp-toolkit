# MSP Toolkit Examples

This directory contains runnable examples demonstrating MSP Toolkit functionality.

## Available Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates core functionality:
- Creating clients
- Listing clients
- Running health checks
- Generating reports
- Client onboarding workflow

**Run**:
```bash
python examples/basic_usage.py
```

### 2. Health Monitoring Workflow (`health_monitoring_workflow.py`)

Shows automated health monitoring for multiple clients:
- Multi-client health checks
- Issue detection and alerting
- Health summaries
- Historical data retrieval

**Run**:
```bash
python examples/health_monitoring_workflow.py
```

## Prerequisites

Before running examples:

1. **Configure MSP Toolkit**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Create config file**:
   ```bash
   mkdir -p config
   # Create config/msp-toolkit.yaml (see README.md)
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   # OR
   poetry install
   ```

## Extending Examples

These examples serve as starting points. You can extend them to:

- Add custom health checks
- Integrate with your RMM platform
- Create custom report templates
- Build automation workflows
- Implement alerting logic

## Need Help?

- See main [README.md](../README.md) for documentation
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup
- Review [ANALYSIS_SUMMARY.md](../ANALYSIS_SUMMARY.md) for architecture details
