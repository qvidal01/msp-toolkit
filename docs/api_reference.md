# API Reference

Complete API documentation for MSP Toolkit.

## Core Classes

### MSPToolkit

Main entry point for the toolkit.

```python
from msp_toolkit import MSPToolkit

toolkit = MSPToolkit.from_config("config.yaml")
```

**Methods**:
- `from_config(config_path: str) -> MSPToolkit` - Create from config file
- `from_dict(config_dict: Dict) -> MSPToolkit` - Create from dictionary
- `get_client_manager() -> ClientManager` - Get client manager
- `get_health_monitor() -> HealthMonitor` - Get health monitor
- `get_report_generator() -> ReportGenerator` - Get report generator
- `health_check() -> Dict` - Check toolkit health

### ClientManager

Manages client lifecycle.

```python
client_mgr = toolkit.get_client_manager()
```

**Methods**:
- `create(client_id, name, **kwargs) -> Client` - Create client
- `get_client(client_id) -> Client` - Get client by ID
- `list_clients(filters=None) -> List[Client]` - List clients
- `update(client_id, **updates) -> Client` - Update client
- `delete(client_id) -> bool` - Delete client
- `onboard(client_id, template) -> Dict` - Run onboarding workflow

### HealthMonitor

System health monitoring.

```python
health_monitor = toolkit.get_health_monitor()
```

**Methods**:
- `run_checks(client_id, check_types=None) -> List[CheckResult]` - Run checks
- `get_history(client_id, days=7) -> List[CheckResult]` - Get check history
- `get_status_summary(client_id) -> HealthSummary` - Get status summary
- `configure(client_id, config) -> bool` - Configure checks

### ReportGenerator

Report generation.

```python
report_gen = toolkit.get_report_generator()
```

**Methods**:
- `generate(client, template, format) -> Report` - Generate report
- `list_templates() -> List[str]` - List available templates
- `add_template(name, content) -> bool` - Add custom template

## Data Models

All models use Pydantic for validation.

### Client

```python
from msp_toolkit.core.models import Client, ClientTier, ClientStatus

client = Client(
    id="acme-corp",
    name="Acme Corp",
    tier=ClientTier.PREMIUM,
    status=ClientStatus.ACTIVE,
)
```

**Fields**:
- `id: str` - Unique identifier
- `name: str` - Company name
- `contact_email: Optional[str]` - Contact email
- `tier: ClientTier` - Service tier (bronze/silver/gold/premium)
- `status: ClientStatus` - Account status
- `metadata: Dict` - Custom fields

### CheckResult

```python
from msp_toolkit.core.models import CheckResult, HealthCheckType, HealthCheckStatus

result = CheckResult(
    check_type=HealthCheckType.CPU,
    status=HealthCheckStatus.HEALTHY,
    message="CPU usage: 45%",
    value=45.0,
)
```

**Fields**:
- `check_type: HealthCheckType` - Type of check
- `status: HealthCheckStatus` - Result status
- `message: str` - Human-readable message
- `value: Optional[float]` - Measured value
- `threshold: Optional[float]` - Threshold checked

## Exceptions

All exceptions inherit from `MSPToolkitError`.

```python
from msp_toolkit.core.exceptions import (
    ClientNotFoundError,
    ConfigurationError,
    IntegrationError,
)

try:
    client = client_mgr.get_client("nonexistent")
except ClientNotFoundError as e:
    print(e.message)  # "Client 'nonexistent' not found"
    print(e.code)     # "CLIENT_NOT_FOUND"
```

## Configuration

Configuration via YAML or environment variables.

```yaml
general:
  company_name: "My MSP"
  log_level: "INFO"

database:
  type: "sqlite"
  path: "data/msp.db"

health_checks:
  thresholds:
    cpu_percent: 85
```

Environment variables override config:
```bash
GENERAL_LOG_LEVEL=DEBUG
DATABASE_PATH=/custom/path/db.sqlite
```

## Integration Base Classes

### RMMAdapter

Base class for RMM integrations.

```python
from msp_toolkit.integrations.rmm.base import RMMAdapter

class MyRMM(RMMAdapter):
    def get_devices(self, client_id):
        # Implementation
        pass
```

**Abstract Methods**:
- `get_devices(client_id) -> List[Device]`
- `deploy_agent(device_id) -> Dict`
- `execute_command(device_id, command) -> Dict`
- `get_alerts(client_id, since) -> List[Dict]`

For complete examples, see the [examples/](../examples/) directory.
