"""
CLI integration smoke tests.
"""

from pathlib import Path

import yaml
from click.testing import CliRunner

from msp_toolkit.cli import cli


def _write_config(base_dir: Path) -> Path:
    """Create a minimal config file for CLI testing."""
    config_dir = base_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "msp-toolkit.yaml"
    db_path = base_dir / "cli-test.db"
    template_dir = base_dir / "templates" / "reports"
    template_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "health-report.html").write_text("<html><body>ok</body></html>", encoding="utf-8")

    yaml.safe_dump(
        {
            "general": {"log_level": "INFO", "company_name": "Test MSP"},
            "database": {"type": "sqlite", "path": str(db_path)},
            "health_checks": {"thresholds": {"cpu_percent": 80, "memory_percent": 85, "disk_percent": 80}},
            "reporting": {"template_dir": str(template_dir), "output_dir": str(base_dir / "reports")},
        },
        config_path.open("w", encoding="utf-8"),
    )
    return config_path


def test_cli_health_check(tmp_path: Path):
    """Health check command should run with provided config."""
    config_path = _write_config(tmp_path)
    runner = CliRunner()

    result = runner.invoke(cli, ["--config", str(config_path), "health", "check", "test-client"])

    assert result.exit_code == 0
    assert "Health Check Results" in result.output


def test_cli_client_add(tmp_path: Path):
    """Client add command should accept tier choices and create a client."""
    config_path = _write_config(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "--config",
            str(config_path),
            "client",
            "add",
            "--name",
            "Acme Corp",
            "--tier",
            "premium",
        ],
    )

    assert result.exit_code == 0
    assert "Client 'Acme Corp' created successfully" in result.output


def test_cli_device_crud(tmp_path: Path):
    """Device add/list/delete round-trip."""
    config_path = _write_config(tmp_path)
    runner = CliRunner()

    # add client first
    runner.invoke(
        cli,
        [
            "--config",
            str(config_path),
            "client",
            "add",
            "--name",
            "Acme Corp",
            "--tier",
            "premium",
        ],
    )

    add_result = runner.invoke(
        cli,
        [
            "--config",
            str(config_path),
            "device",
            "add",
            "--client-id",
            "acme-corp",
            "--name",
            "server-1",
            "--type",
            "server",
        ],
    )
    assert add_result.exit_code == 0
    assert "Device 'server-1' added" in add_result.output

    list_result = runner.invoke(
        cli,
        [
            "--config",
            str(config_path),
            "device",
            "list",
            "--client-id",
            "acme-corp",
        ],
    )
    assert "server-1" in list_result.output

    # extract ID from output
    device_id_line = next(line for line in list_result.output.splitlines() if "server-1" in line)
    device_id = int(device_id_line.split("ID:")[1].split(",")[0].strip())

    delete_result = runner.invoke(
        cli,
        [
            "--config",
            str(config_path),
            "device",
            "delete",
            str(device_id),
        ],
    )
    assert delete_result.exit_code == 0
    assert f"Device {device_id} deleted" in delete_result.output
