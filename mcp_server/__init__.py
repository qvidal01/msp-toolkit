"""
MCP Server for MSP Toolkit.

This module implements a Model Context Protocol server that exposes
MSP Toolkit functionality to AI agents like Claude.
"""

from mcp_server.server import MCPServer, run_server

__all__ = ["MCPServer", "run_server"]
