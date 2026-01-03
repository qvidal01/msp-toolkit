"""
Report generation functionality.

This module handles creation of client reports using templates
and various output formats (PDF, HTML, Markdown).
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog
from jinja2 import Environment, FileSystemLoader

from msp_toolkit.core.models import Client, Report, ReportFormat, ReportTemplate
from msp_toolkit.utils.config import Config

logger = structlog.get_logger(__name__)


class ReportGenerator:
    """
    Generates client reports from templates.

    Supports multiple output formats and customizable templates for
    different report types (monthly summaries, health reports, etc.).

    Example:
        >>> config = Config.from_file("config.yaml")
        >>> generator = ReportGenerator(config)
        >>> report = generator.generate(
        ...     client=client,
        ...     template=ReportTemplate.MONTHLY_SUMMARY,
        ...     format=ReportFormat.PDF
        ... )
        >>> report.save("reports/acme-corp-2024-01.pdf")
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize ReportGenerator.

        Args:
            config: Configuration object

        Raises:
            ConfigurationError: If template directory not found
        """
        self.config = config
        self.template_dir = Path(config.get("reporting.template_dir", "templates/reports"))
        self.output_dir = Path(config.get("reporting.output_dir", "reports"))

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Set up Jinja2 environment
        if self.template_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=True,
            )
        else:
            logger.warning(
                "Template directory not found",
                template_dir=str(self.template_dir),
            )
            self.jinja_env = None

        logger.info("ReportGenerator initialized")

    def generate(
        self,
        client: Client,
        template: ReportTemplate,
        format: ReportFormat = ReportFormat.PDF,
        data: dict | None = None,
        health_summary: dict[str, Any] | None = None,
        recent_checks: list[dict[str, Any]] | None = None,
        alerts: list[dict[str, Any]] | None = None,
        tickets: list[dict[str, Any]] | None = None,
    ) -> Report:
        """
        Generate a report for a client.

        Args:
            client: Client object
            template: Report template to use
            format: Output format
            data: Additional data for the report

        Returns:
            Report object with metadata

        Example:
            >>> report = generator.generate(
            ...     client=client,
            ...     template=ReportTemplate.MONTHLY_SUMMARY,
            ...     format=ReportFormat.PDF,
            ...     data={"month": "2024-01"}
            ... )
        """
        logger.info(
            "Generating report",
            client_id=client.id,
            template=template.value,
            format=format.value,
        )

        # Prepare report data
        report_data = self._prepare_data(
            client,
            data or {},
            health_summary=health_summary,
            recent_checks=recent_checks,
            alerts=alerts,
            tickets=tickets,
        )

        # Render template
        rendered_content = self._render_template(template, report_data)

        # Convert to target format
        file_path = self._convert_format(
            rendered_content,
            client.id,
            template,
            format,
        )

        # Create report metadata
        report = Report(
            client_id=client.id,
            template=template,
            format=format,
            file_path=str(file_path),
            data=report_data,
        )

        logger.info(
            "Report generated successfully",
            client_id=client.id,
            file_path=str(file_path),
        )

        return report

    def _prepare_data(
        self,
        client: Client,
        additional_data: dict,
        health_summary: dict[str, Any] | None = None,
        recent_checks: list[dict[str, Any]] | None = None,
        alerts: list[dict[str, Any]] | None = None,
        tickets: list[dict[str, Any]] | None = None,
    ) -> dict:
        """
        Prepare data for report rendering.

        Args:
            client: Client object
            additional_data: Additional data to include

        Returns:
            Dictionary with all report data
        """
        data = {
            "client": {
                "id": client.id,
                "name": client.name,
                "tier": client.tier.value,
                "contact_email": client.contact_email,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "report_period": additional_data.get("period", "current"),
            "health_summary": health_summary or {},
            "recent_checks": recent_checks or [],
            "alerts": alerts or [],
            "tickets": tickets or [],
        }

        # TODO: Add health check data, alerts, incidents, etc.
        data.update(additional_data)

        return data

    def _render_template(
        self,
        template: ReportTemplate,
        data: dict,
    ) -> str:
        """
        Render report template with data.

        Args:
            template: Report template
            data: Data dictionary

        Returns:
            Rendered HTML/Markdown content
        """
        if self.jinja_env is None:
            # Fallback to basic template
            return self._get_fallback_template(template, data)

        try:
            template_file = f"{template.value}.html"
            jinja_template = self.jinja_env.get_template(template_file)
            return jinja_template.render(**data)
        except Exception as e:
            logger.warning(
                "Failed to load template, using fallback",
                template=template.value,
                error=str(e),
            )
            return self._get_fallback_template(template, data)

    def _get_fallback_template(self, template: ReportTemplate, data: dict) -> str:
        """Generate a basic fallback template."""
        client_name = data["client"]["name"]
        period = data.get("report_period", "current")

        return f"""
        <html>
        <head><title>{template.value.replace('-', ' ').title()} - {client_name}</title></head>
        <body>
            <h1>{template.value.replace('-', ' ').title()}</h1>
            <h2>Client: {client_name}</h2>
            <p>Period: {period}</p>
            <p>Generated: {data["generated_at"]}</p>
            <p><em>Note: Using fallback template. Configure template_dir in config for custom reports.</em></p>
        </body>
        </html>
        """

    def _convert_format(
        self,
        content: str,
        client_id: str,
        template: ReportTemplate,
        format: ReportFormat,
    ) -> Path:
        """
        Convert rendered content to target format.

        Args:
            content: Rendered HTML/Markdown content
            client_id: Client identifier
            template: Report template
            format: Target format

        Returns:
            Path to generated file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        filename = f"{client_id}-{template.value}-{timestamp}.{format.value}"
        file_path = self.output_dir / filename

        if format == ReportFormat.HTML:
            file_path.write_text(content, encoding="utf-8")

        elif format == ReportFormat.MARKDOWN:
            # TODO: Convert HTML to Markdown
            markdown_content = content  # Placeholder
            file_path.write_text(markdown_content, encoding="utf-8")

        elif format == ReportFormat.PDF:
            # TODO: Implement PDF generation using weasyprint
            # For now, save as HTML
            logger.warning("PDF generation not yet implemented, saving as HTML")
            file_path = file_path.with_suffix(".html")
            file_path.write_text(content, encoding="utf-8")

        return file_path

    def list_templates(self) -> list[str]:
        """
        List available report templates.

        Returns:
            List of template names
        """
        if self.jinja_env is None or not self.template_dir.exists():
            return [t.value for t in ReportTemplate]

        templates = [
            f.stem for f in self.template_dir.glob("*.html")
        ]
        return templates

    def add_template(
        self,
        name: str,
        template_content: str,
    ) -> bool:
        """
        Add a custom report template.

        Args:
            name: Template name
            template_content: Template content (Jinja2 HTML)

        Returns:
            True if added successfully
        """
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True, exist_ok=True)

        template_path = self.template_dir / f"{name}.html"
        template_path.write_text(template_content, encoding="utf-8")

        logger.info("Custom template added", name=name)
        return True
