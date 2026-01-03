"""
MCP tool definitions and handlers.

This module defines the tools exposed via MCP and their implementation.
"""

from typing import Any

from msp_toolkit import MSPToolkit
from msp_toolkit.core.models import ClientTier, ReportFormat, ReportTemplate

# Tool schemas following MCP specification
TOOL_SCHEMAS = [
    {
        "name": "client_list",
        "description": "List MSP clients with optional filtering by tier, status, or name",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tier": {
                    "type": "string",
                    "enum": ["bronze", "silver", "gold", "premium"],
                    "description": "Filter by client tier",
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "inactive", "suspended"],
                    "description": "Filter by client status",
                },
                "search": {
                    "type": "string",
                    "description": "Search clients by name",
                },
            },
        },
    },
    {
        "name": "client_onboard",
        "description": "Onboard a new MSP client with automated setup",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Client company name",
                },
                "contact_email": {
                    "type": "string",
                    "description": "Primary contact email",
                },
                "tier": {
                    "type": "string",
                    "enum": ["bronze", "silver", "gold", "premium"],
                    "description": "Service tier",
                },
                "template": {
                    "type": "string",
                    "enum": ["basic", "standard-business", "enterprise"],
                    "description": "Onboarding template",
                    "default": "standard-business",
                },
            },
            "required": ["name", "tier"],
        },
    },
    {
        "name": "health_check",
        "description": "Run health checks for one or all clients",
        "inputSchema": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "Specific client ID (omit for all clients)",
                },
                "check_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["cpu", "memory", "disk", "services", "network"],
                    },
                    "description": "Specific check types to run",
                },
            },
        },
    },
    {
        "name": "report_generate",
        "description": "Generate reports for clients",
        "inputSchema": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "Client ID",
                },
                "template": {
                    "type": "string",
                    "enum": [
                        "monthly-summary",
                        "health-report",
                        "sla-compliance",
                        "incident-summary",
                    ],
                    "description": "Report template",
                },
                "format": {
                    "type": "string",
                    "enum": ["pdf", "html", "markdown"],
                    "default": "pdf",
                },
            },
            "required": ["client_id", "template"],
        },
    },
    {
        "name": "device_list",
        "description": "List devices, optionally filtered by client",
        "inputSchema": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "Client ID to filter devices",
                }
            },
        },
    },
    {
        "name": "device_add",
        "description": "Register a device for a client",
        "inputSchema": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "Client ID"},
                "name": {"type": "string", "description": "Device name/hostname"},
                "type": {
                    "type": "string",
                    "description": "Device type (server, workstation, etc.)",
                    "default": "workstation",
                },
                "rmm_device_id": {
                    "type": "string",
                    "description": "RMM device identifier",
                },
            },
            "required": ["client_id", "name"],
        },
    },
]


def handle_client_list(toolkit: MSPToolkit, arguments: dict[str, Any]) -> str:
    """
    Handle client_list tool invocation.

    Args:
        toolkit: MSPToolkit instance
        arguments: Tool arguments

    Returns:
        Formatted response text
    """
    client_mgr = toolkit.get_client_manager()

    # Build filters
    filters = {}
    if "tier" in arguments:
        filters["tier"] = arguments["tier"]
    if "status" in arguments:
        filters["status"] = arguments["status"]

    clients = client_mgr.list_clients(filters=filters)

    if not clients:
        return "No clients found."

    # Format response
    lines = [f"Found {len(clients)} client(s):\n"]
    for client in clients:
        lines.append(f"• {client.name}")
        lines.append(f"  - ID: {client.id}")
        lines.append(f"  - Tier: {client.tier.value}")
        lines.append(f"  - Status: {client.status.value}")
        if client.contact_email:
            lines.append(f"  - Contact: {client.contact_email}")
        lines.append("")

    return "\n".join(lines)


def handle_client_onboard(toolkit: MSPToolkit, arguments: dict[str, Any]) -> str:
    """
    Handle client_onboard tool invocation.

    Args:
        toolkit: MSPToolkit instance
        arguments: Tool arguments

    Returns:
        Formatted response text
    """
    client_mgr = toolkit.get_client_manager()

    name = arguments["name"]
    tier = arguments["tier"]
    contact_email = arguments.get("contact_email")
    template = arguments.get("template", "standard-business")

    # Generate client ID from name
    client_id = name.lower().replace(" ", "-").replace(".", "")

    # Create client
    client = client_mgr.create(
        client_id=client_id,
        name=name,
        contact_email=contact_email,
        tier=ClientTier(tier),
    )

    # Run onboarding
    result = client_mgr.onboard(client_id, template=template)

    # Format response
    lines = [
        f"✓ Client '{name}' onboarded successfully\n",
        "Client Details:",
        f"  - ID: {client.id}",
        f"  - Name: {client.name}",
        f"  - Tier: {client.tier.value}",
        f"  - Template: {template}\n",
        f"Onboarding Status: {result['status']}",
        "\nSteps Completed:",
    ]

    for step in result.get("steps_completed", []):
        lines.append(f"  ✓ {step}")

    return "\n".join(lines)


def handle_health_check(toolkit: MSPToolkit, arguments: dict[str, Any]) -> str:
    """
    Handle health_check tool invocation.

    Args:
        toolkit: MSPToolkit instance
        arguments: Tool arguments

    Returns:
        Formatted response text
    """
    health_monitor = toolkit.get_health_monitor()

    client_id = arguments.get("client_id")
    check_types = arguments.get("check_types")

    if not client_id:
        return "Error: client_id is required"

    # Run checks
    results = health_monitor.run_checks(client_id, check_types=check_types)

    # Format response
    lines = [f"Health Check Results for '{client_id}':\n"]

    for result in results:
        status_icon = "✓" if result.status.value == "healthy" else "⚠"
        lines.append(f"{status_icon} {result.check_type.value}: {result.message}")

    # Add summary
    summary = health_monitor.get_status_summary(client_id)
    lines.append("\nSummary:")
    lines.append(f"  Total Checks: {summary.total_checks}")
    lines.append(f"  Healthy: {summary.healthy}")
    lines.append(f"  Warnings: {summary.warnings}")
    lines.append(f"  Critical: {summary.critical}")

    return "\n".join(lines)


def handle_report_generate(toolkit: MSPToolkit, arguments: dict[str, Any]) -> str:
    """
    Handle report_generate tool invocation.

    Args:
        toolkit: MSPToolkit instance
        arguments: Tool arguments

    Returns:
        Formatted response text
    """
    client_mgr = toolkit.get_client_manager()
    report_gen = toolkit.get_report_generator()
    health_monitor = toolkit.get_health_monitor()

    client_id = arguments["client_id"]
    template = arguments["template"]
    format_type = arguments.get("format", "pdf")

    # Get client
    client = client_mgr.get_client(client_id)
    summary = health_monitor.get_status_summary(client_id)
    recent_checks = health_monitor.get_history(client_id, days=30)

    # Generate report
    report = report_gen.generate(
        client=client,
        template=ReportTemplate(template),
        format=ReportFormat(format_type),
        health_summary=summary.model_dump(),
        recent_checks=[r.model_dump() for r in recent_checks],
    )

    # Format response
    lines = [
        "✓ Report generated successfully\n",
        "Report Details:",
        f"  - Client: {client.name}",
        f"  - Template: {template}",
        f"  - Format: {format_type}",
        f"  - File: {report.file_path}",
        f"  - Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
    ]

    return "\n".join(lines)


def handle_device_list(toolkit: MSPToolkit, arguments: dict[str, Any]) -> str:
    """Handle device_list tool invocation."""
    device_mgr = toolkit.get_device_manager()
    devices = device_mgr.list_devices(client_id=arguments.get("client_id"))

    if not devices:
        return "No devices found."

    lines = [f"Found {len(devices)} device(s):\n"]
    for device in devices:
        lines.append(f"• {device.name} (ID: {device.id})")
        lines.append(f"  - Client: {device.client_id}")
        lines.append(f"  - Type: {device.type}")
        if device.rmm_device_id:
            lines.append(f"  - RMM ID: {device.rmm_device_id}")
        if device.last_seen:
            lines.append(f"  - Last Seen: {device.last_seen}")
        lines.append("")
    return "\n".join(lines)


def handle_device_add(toolkit: MSPToolkit, arguments: dict[str, Any]) -> str:
    """Handle device_add tool invocation."""
    device_mgr = toolkit.get_device_manager()
    device = device_mgr.add_device(
        client_id=arguments["client_id"],
        name=arguments["name"],
        type=arguments.get("type", "workstation"),
        rmm_device_id=arguments.get("rmm_device_id"),
    )

    lines = [
        "✓ Device registered",
        f"  - ID: {device.id}",
        f"  - Name: {device.name}",
        f"  - Client: {device.client_id}",
        f"  - Type: {device.type}",
    ]
    return "\n".join(lines)
