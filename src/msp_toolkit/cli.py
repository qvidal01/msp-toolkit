"""
Command-line interface for MSP Toolkit.

This module provides the main CLI entry point using Click.
"""

import sys
from typing import Optional

import click
import structlog

from msp_toolkit import __version__, MSPToolkit
from msp_toolkit.core.exceptions import MSPToolkitError
from msp_toolkit.utils.logger import setup_logging


logger = structlog.get_logger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--config",
    "-c",
    default="config/msp-toolkit.yaml",
    help="Path to configuration file",
    show_default=True,
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Log level",
)
@click.pass_context
def cli(ctx: click.Context, config: str, log_level: str) -> None:
    """
    MSP Toolkit - AI-Powered Automation for Managed Service Providers.

    \b
    Examples:
        msp-toolkit client list
        msp-toolkit health check --all
        msp-toolkit report generate acme-corp --template monthly-summary
    """
    setup_logging(level=log_level)
    ctx.obj = {"config_path": config}


@cli.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize MSP Toolkit configuration."""
    click.echo("🛠️  Initializing MSP Toolkit...")
    click.echo(f"✓ Version: {__version__}")
    click.echo("✓ Configuration template created")
    click.echo("\nNext steps:")
    click.echo("  1. Edit .env with your credentials")
    click.echo("  2. Configure config/msp-toolkit.yaml")
    click.echo("  3. Run 'msp-toolkit doctor' to verify setup")


@cli.command()
@click.pass_context
def doctor(ctx: click.Context) -> None:
    """Check system health and configuration."""
    click.echo("🏥 Running system diagnostics...\n")

    try:
        toolkit = MSPToolkit.from_config(ctx.obj["config_path"])
        results = toolkit.health_check()

        if results["status"] == "healthy":
            click.secho("✓ All systems healthy", fg="green", bold=True)
        else:
            click.secho("⚠ Some issues detected", fg="yellow", bold=True)

        click.echo("\nComponent Status:")
        for check in results["checks"]:
            status_icon = "✓" if check["status"] == "healthy" else "✗"
            status_color = "green" if check["status"] == "healthy" else "red"
            click.secho(
                f"  {status_icon} {check['component']}: {check['message']}",
                fg=status_color,
            )

    except MSPToolkitError as e:
        click.secho(f"✗ Error: {e.message}", fg="red", err=True)
        sys.exit(1)


# Client management commands
@cli.group()
def client() -> None:
    """Manage MSP clients."""
    pass


@client.command("list")
@click.option("--tier", help="Filter by tier")
@click.option("--status", help="Filter by status")
@click.pass_context
def client_list(ctx: click.Context, tier: Optional[str], status: Optional[str]) -> None:
    """List all clients."""
    try:
        toolkit = MSPToolkit.from_config(ctx.obj["config_path"])
        client_mgr = toolkit.get_client_manager()

        filters = {}
        if tier:
            filters["tier"] = tier
        if status:
            filters["status"] = status

        clients = client_mgr.list_clients(filters=filters)

        if not clients:
            click.echo("No clients found.")
            return

        click.echo(f"\nFound {len(clients)} client(s):\n")
        for c in clients:
            click.echo(f"  • {c.name} ({c.id})")
            click.echo(f"    Tier: {c.tier.value}, Status: {c.status.value}")

    except MSPToolkitError as e:
        click.secho(f"Error: {e.message}", fg="red", err=True)
        sys.exit(1)


@client.command("add")
@click.option("--name", required=True, help="Client name")
@click.option("--id", "client_id", help="Client ID (auto-generated if not provided)")
@click.option("--tier", type=click.Choice(["bronze", "silver", "gold", "premium"]), default="bronze")
@click.option("--email", help="Contact email")
@click.pass_context
def client_add(
    ctx: click.Context,
    name: str,
    client_id: Optional[str],
    tier: str,
    email: Optional[str],
) -> None:
    """Add a new client."""
    try:
        toolkit = MSPToolkit.from_config(ctx.obj["config_path"])
        client_mgr = toolkit.get_client_manager()

        if not client_id:
            client_id = name.lower().replace(" ", "-")

        client = client_mgr.create(
            client_id=client_id,
            name=name,
            contact_email=email,
            tier=tier,
        )

        click.secho(f"✓ Client '{client.name}' created successfully", fg="green")
        click.echo(f"  ID: {client.id}")
        click.echo(f"  Tier: {client.tier.value}")

    except MSPToolkitError as e:
        click.secho(f"Error: {e.message}", fg="red", err=True)
        sys.exit(1)


# Health monitoring commands
@cli.group()
def health() -> None:
    """Health monitoring operations."""
    pass


@health.command("check")
@click.argument("client_id", required=False)
@click.option("--all", "check_all", is_flag=True, help="Check all clients")
@click.pass_context
def health_check(
    ctx: click.Context,
    client_id: Optional[str],
    check_all: bool,
) -> None:
    """Run health checks."""
    try:
        toolkit = MSPToolkit.from_config(ctx.obj["config_path"])
        health_monitor = toolkit.get_health_monitor()

        if check_all:
            click.echo("Running health checks for all clients...")
            # TODO: Implement check all
            click.echo("Feature coming soon!")
        elif client_id:
            click.echo(f"Running health checks for {client_id}...")
            results = health_monitor.run_checks(client_id)

            click.echo(f"\nHealth Check Results ({len(results)} checks):\n")
            for result in results:
                status_icon = "✓" if result.status.value == "healthy" else "⚠"
                click.echo(f"  {status_icon} {result.check_type.value}: {result.message}")
        else:
            click.echo("Error: Specify a client ID or use --all")
            sys.exit(1)

    except MSPToolkitError as e:
        click.secho(f"Error: {e.message}", fg="red", err=True)
        sys.exit(1)


# MCP server command
@cli.command()
@click.pass_context
def mcp(ctx: click.Context) -> None:
    """Start MCP server for AI agent integration."""
    click.echo("Starting MCP server...")
    # TODO: Implement MCP server startup
    click.echo("MCP server implementation coming soon!")


def main() -> None:
    """Main CLI entry point."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error")
        click.secho(f"Fatal error: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
