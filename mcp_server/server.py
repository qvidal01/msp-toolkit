"""
MCP Server implementation for MSP Toolkit.

This server exposes toolkit functionality via the Model Context Protocol,
enabling AI-powered automation workflows.
"""

import asyncio
from typing import Any

import structlog
from mcp import StdioServerParameters
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_server.tools import (
    TOOL_SCHEMAS,
    handle_client_list,
    handle_client_onboard,
    handle_device_add,
    handle_device_list,
    handle_health_check,
    handle_report_generate,
)
from msp_toolkit import MSPToolkit
from msp_toolkit.core.exceptions import MSPToolkitError
from msp_toolkit.utils.logger import setup_logging

logger = structlog.get_logger(__name__)


class MCPServer:
    """
    MCP Server for MSP Toolkit.

    Implements the Model Context Protocol to expose toolkit functionality
    to AI agents.

    Example:
        >>> server = MCPServer("config/msp-toolkit.yaml")
        >>> await server.run()
    """

    def __init__(self, config_path: str) -> None:
        """
        Initialize MCP Server.

        Args:
            config_path: Path to MSP Toolkit configuration file
        """
        self.config_path = config_path
        self.toolkit: MSPToolkit | None = None
        self.server = Server("msp-toolkit")

        # Register tool handlers
        self._register_handlers()

        logger.info("MCP Server initialized", config_path=config_path)

    def _register_handlers(self) -> None:
        """Register MCP tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [Tool(**schema) for schema in TOOL_SCHEMAS]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """
            Handle tool invocation.

            Args:
                name: Tool name
                arguments: Tool arguments

            Returns:
                List of text content responses
            """
            try:
                # Initialize toolkit if needed
                if self.toolkit is None:
                    self.toolkit = MSPToolkit.from_config(self.config_path)

                logger.info("Tool called", tool=name, arguments=arguments)

                # Route to appropriate handler
                if name == "client_list":
                    result = handle_client_list(self.toolkit, arguments)
                elif name == "client_onboard":
                    result = handle_client_onboard(self.toolkit, arguments)
                elif name == "health_check":
                    result = handle_health_check(self.toolkit, arguments)
                elif name == "report_generate":
                    result = handle_report_generate(self.toolkit, arguments)
                elif name == "device_list":
                    result = handle_device_list(self.toolkit, arguments)
                elif name == "device_add":
                    result = handle_device_add(self.toolkit, arguments)
                else:
                    result = f"Unknown tool: {name}"

                return [TextContent(type="text", text=result)]

            except MSPToolkitError as e:
                error_msg = f"Error: {e.message}"
                logger.error("Tool execution failed", tool=name, error=e.message)
                return [TextContent(type="text", text=error_msg)]

            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.exception("Unexpected error in tool execution")
                return [TextContent(type="text", text=error_msg)]

async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting MCP server")

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                StdioServerParameters(),
            )


async def run_server(config_path: str, log_level: str | None = None) -> None:
    """Run MCP server with provided configuration path."""
    import os

    setup_logging(level=log_level or os.getenv("MCP_LOG_LEVEL", "INFO"))
    server = MCPServer(config_path)
    await server.run()


async def main() -> None:
    """Main entry point for MCP server."""
    import os

    await run_server(
        config_path=os.getenv("MSP_CONFIG", "config/msp-toolkit.yaml"),
        log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
    )


if __name__ == "__main__":
    asyncio.run(main())
