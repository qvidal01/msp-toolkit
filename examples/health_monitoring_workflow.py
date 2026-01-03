"""
Health Monitoring Workflow Example

Demonstrates automated health monitoring for multiple clients with
threshold checking and alerting.
"""

from msp_toolkit import MSPToolkit
from msp_toolkit.core.models import ClientTier, HealthCheckStatus, HealthCheckType


def main():
    print("🏥 Health Monitoring Workflow Example\n")

    # Initialize toolkit
    toolkit = MSPToolkit.from_config("config/msp-toolkit.yaml")
    client_mgr = toolkit.get_client_manager()
    health_monitor = toolkit.get_health_monitor()

    # Create sample clients
    print("📋 Setting up sample clients...")
    clients = [
        client_mgr.create("client-a", name="Client A", tier=ClientTier.BRONZE),
        client_mgr.create("client-b", name="Client B", tier=ClientTier.PREMIUM),
        client_mgr.create("client-c", name="Client C", tier=ClientTier.GOLD),
    ]
    print(f"✓ Created {len(clients)} clients\n")

    # Run health checks for all clients
    print("🔍 Running health checks for all clients...\n")

    issues_found = []

    for client in clients:
        print(f"Checking {client.name}...")

        # Run all health checks
        results = health_monitor.run_checks(
            client.id,
            check_types=[
                HealthCheckType.CPU,
                HealthCheckType.MEMORY,
                HealthCheckType.DISK,
            ]
        )

        # Analyze results
        for result in results:
            if result.status == HealthCheckStatus.WARNING:
                issues_found.append({
                    "client": client.name,
                    "check": result.check_type.value,
                    "status": result.status.value,
                    "message": result.message,
                })
                print(f"  ⚠ WARNING: {result.check_type.value} - {result.message}")
            elif result.status == HealthCheckStatus.CRITICAL:
                issues_found.append({
                    "client": client.name,
                    "check": result.check_type.value,
                    "status": result.status.value,
                    "message": result.message,
                })
                print(f"  🚨 CRITICAL: {result.check_type.value} - {result.message}")
            else:
                print(f"  ✓ {result.check_type.value}: {result.message}")

        # Get summary
        summary = health_monitor.get_status_summary(client.id)
        print(f"  Summary: {summary.healthy} healthy, {summary.warnings} warnings, {summary.critical} critical\n")

    # Report issues
    print("\n📊 Health Monitoring Summary")
    print("=" * 50)

    if issues_found:
        print(f"\n⚠ Found {len(issues_found)} issue(s):\n")
        for issue in issues_found:
            print(f"• {issue['client']}: {issue['check']} - {issue['status']}")
            print(f"  {issue['message']}")
    else:
        print("\n✓ All systems healthy!")

    # Demonstrate historical data
    print("\n📈 Retrieving health check history...")
    for client in clients:
        history = health_monitor.get_history(client.id, days=7)
        print(f"  {client.name}: {len(history)} checks in last 7 days")

    print("\n✅ Health monitoring workflow completed!")


if __name__ == "__main__":
    main()
