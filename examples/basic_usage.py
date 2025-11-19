"""
Basic MSP Toolkit Usage Example

This example demonstrates the core functionality of MSP Toolkit including
client management, health monitoring, and report generation.
"""

from msp_toolkit import MSPToolkit
from msp_toolkit.core.models import ClientTier

def main():
    # Initialize toolkit from config file
    print("🛠️  Initializing MSP Toolkit...")
    toolkit = MSPToolkit.from_config("config/msp-toolkit.yaml")

    # Get managers
    client_mgr = toolkit.get_client_manager()
    health_monitor = toolkit.get_health_monitor()
    report_gen = toolkit.get_report_generator()

    # 1. Create a new client
    print("\n📋 Creating new client...")
    client = client_mgr.create(
        client_id="demo-client",
        name="Demo Company Inc",
        contact_email="admin@demo.com",
        tier=ClientTier.PREMIUM,
    )
    print(f"✓ Created client: {client.name} ({client.id})")

    # 2. List all clients
    print("\n👥 Listing all clients...")
    all_clients = client_mgr.list_clients()
    for c in all_clients:
        print(f"  • {c.name} - {c.tier.value} tier")

    # 3. Run health checks
    print(f"\n🏥 Running health checks for {client.id}...")
    results = health_monitor.run_checks(client.id)
    for result in results:
        status_icon = "✓" if result.status.value == "healthy" else "⚠"
        print(f"  {status_icon} {result.check_type.value}: {result.message}")

    # 4. Get health summary
    print("\n📊 Health Summary:")
    summary = health_monitor.get_status_summary(client.id)
    print(f"  Total checks: {summary.total_checks}")
    print(f"  Healthy: {summary.healthy}")
    print(f"  Warnings: {summary.warnings}")
    print(f"  Critical: {summary.critical}")

    # 5. Generate report
    print(f"\n📄 Generating report...")
    from msp_toolkit.core.models import ReportTemplate, ReportFormat

    report = report_gen.generate(
        client=client,
        template=ReportTemplate.MONTHLY_SUMMARY,
        format=ReportFormat.HTML,
    )
    print(f"✓ Report generated: {report.file_path}")

    # 6. Onboard client
    print(f"\n🚀 Running onboarding workflow...")
    onboarding_result = client_mgr.onboard(client.id, template="standard-business")
    print(f"Status: {onboarding_result['status']}")
    print("Steps completed:")
    for step in onboarding_result['steps_completed']:
        print(f"  ✓ {step}")

    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    main()
