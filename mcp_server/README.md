# MSP Toolkit MCP Server

This directory contains the Model Context Protocol (MCP) server implementation for MSP Toolkit, enabling AI-powered automation through Claude and other MCP-compatible clients.

## Features

The MCP server exposes the following tools to AI agents:

- **`client_list`** - List and filter MSP clients
- **`client_onboard`** - Automate new client onboarding
- **`health_check`** - Run system health checks
- **`report_generate`** - Generate client reports

## Setup

### 1. Configure Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "msp-toolkit": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "MSP_CONFIG": "/full/path/to/config/msp-toolkit.yaml",
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 2. Restart Claude Desktop

After adding the configuration, restart Claude Desktop for the changes to take effect.

### 3. Verify Connection

In Claude Desktop, you should see "msp-toolkit" listed in the available tools. Try:

```
List all my premium tier clients
```

## Usage Examples

### List Clients

```
Show me all active clients
```

```
List premium tier clients
```

### Onboard New Client

```
Onboard a new client called "Acme Corp" with email admin@acmecorp.com on the premium tier using the enterprise template
```

### Run Health Checks

```
Run health checks for acme-corp and summarize the results
```

```
Check CPU and memory for acme-corp
```

### Generate Reports

```
Generate a monthly summary report for acme-corp in PDF format
```

## Development

### Running Standalone

For testing, you can run the MCP server standalone:

```bash
# Set environment variables
export MSP_CONFIG="config/msp-toolkit.yaml"
export MCP_LOG_LEVEL="DEBUG"

# Run server
python -m mcp_server.server
```

### Adding New Tools

1. Add tool schema to `tools.py` in `TOOL_SCHEMAS`
2. Implement handler function in `tools.py`
3. Register handler in `server.py`
4. Update this README with usage examples

## Troubleshooting

### Server Not Showing in Claude

- Check Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log` (macOS)
- Verify configuration file syntax (valid JSON)
- Ensure full absolute paths are used
- Restart Claude Desktop

### Tool Execution Errors

- Check `MSP_CONFIG` points to valid configuration file
- Verify credentials are set in `.env`
- Check MCP logs for detailed error messages

### Debugging

Enable debug logging:

```json
{
  "env": {
    "MCP_LOG_LEVEL": "DEBUG"
  }
}
```

## Architecture

```
Claude Desktop
    ↓ (stdio)
MCP Server (mcp_server/server.py)
    ↓
Tool Handlers (mcp_server/tools.py)
    ↓
MSP Toolkit Core (src/msp_toolkit/)
    ↓
RMM/Backup/PSA Integrations
```

## Security Notes

- MCP server runs locally on your machine
- All credentials are managed securely via OS keyring or environment variables
- No data is sent to external servers except configured integrations (RMM, etc.)
- Audit logging tracks all tool invocations

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Desktop MCP Setup](https://modelcontextprotocol.io/quickstart/user)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
