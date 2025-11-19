# Agent Flows MCP Server

A Model Context Protocol (MCP) server that dynamically provides tools based on Agent Flows available in a user's RealTimeX instance. Each flow becomes a callable tool, enabling AI agents to execute complex workflows through simple tool calls.

## Features

- **Dynamic Tool Generation**: Automatically converts Agent Flows into MCP tools
- **Structured Output**: Returns structured JSON data instead of text for programmatic consumption
- **Parameter Extraction**: Automatically extracts tool parameters from flow START steps
- **Flow Caching**: Intelligent caching with TTL for optimal performance
- **Error Handling**: Proper exception handling with detailed error information
- **Type Safety**: Full type hints and Pydantic validation
- **System Variables Support**: Fetches context variables from a local API on every tool invocation and merges them into the request

## Quick Start

### Installation

```bash
# Install via pip
pip install agent-flows-mcp-server

# Or use with uvx (no installation required)
uvx agent-flows-mcp-server
```

### Configuration

Set required environment variables:

```bash
# Required - RealTimeX Configuration
export AGENT_FLOWS_API_KEY="your-realtimex-api-key"

# Required - LLM Configuration
export LITELLM_API_KEY="your-llm-api-key"
export LITELLM_API_BASE="https://api.openai.com/v1"

# Required - MCP ACI Integration
export MCP_ACI_API_KEY="your-aci-api-key"
export MCP_ACI_LINKED_ACCOUNT_OWNER_ID="your-account-owner-id"

# Optional - RealTimeX Instance (defaults to https://marketplace-api.realtimex.ai)
export AGENT_FLOWS_BASE_URL="https://your-custom-instance.com"

# Optional - Override system variables API URL (defaults to http://localhost:3001/api/system/prompt-variables)
export SYSTEM_VARIABLES_API_URL="http://localhost:3001/api/system/prompt-variables"
```

### CLI Options

The server supports several command-line options:

```bash
# Basic usage
uvx agent-flows-mcp-server

# With specific flows only (comma-separated UUIDs)
uvx agent-flows-mcp-server --flows "uuid1,uuid2,uuid3"

# With custom log level
uvx agent-flows-mcp-server --log-level DEBUG

# With configuration file
uvx agent-flows-mcp-server --config /path/to/config.json

# Combined options
uvx agent-flows-mcp-server --flows "uuid1,uuid2" --log-level INFO
```

#### CLI Options Reference

- `--flows`: Comma-separated list of flow UUIDs to expose as tools. If not provided, all available flows will be used.
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR). Default: INFO
- `--config`: Path to configuration file for advanced settings

### MCP Client Configuration

#### Python MCP Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_agent_flows():
    server_params = StdioServerParameters(
        command="uvx",
        args=["agent-flows-mcp-server"],
        env={
            "AGENT_FLOWS_API_KEY": "your-api-key",
            "LITELLM_API_KEY": "your-llm-key",
            "LITELLM_API_BASE": "https://api.openai.com/v1",
            "MCP_ACI_API_KEY": "your-aci-key",
            "MCP_ACI_LINKED_ACCOUNT_OWNER_ID": "your-account-id"
            # "AGENT_FLOWS_BASE_URL": "https://your-custom-instance.com"  # Optional
        }
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available flow tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")

            # Execute a flow tool
            result = await session.call_tool("customer_onboarding_flow", {
                "customer_name": "John Doe",
                "email": "john@example.com",
                "company": "Acme Corp"
            })

            # Access structured result
            if hasattr(result, "structuredContent") and result.structuredContent:
                flow_result = result.structuredContent
                print(f"Success: {flow_result['success']}")
                print(f"Steps executed: {flow_result['steps_executed']}")
                print(f"Execution time: {flow_result['execution_time']}s")
                if flow_result['success']:
                    print(f"Output: {flow_result['output']}")
                else:
                    print(f"Error: {flow_result['error_summary']}")

asyncio.run(use_agent_flows())
```

#### Claude Desktop

```json
{
  "mcpServers": {
    "agent-flows": {
      "command": "uvx",
      "args": ["agent-flows-mcp-server"],
      "env": {
        "AGENT_FLOWS_API_KEY": "your-api-key",
        "LITELLM_API_KEY": "your-llm-key",
        "LITELLM_API_BASE": "https://api.openai.com/v1",
        "MCP_ACI_API_KEY": "your-aci-key",
        "MCP_ACI_LINKED_ACCOUNT_OWNER_ID": "your-account-id"
      }
    }
  }
}
```

To use only specific flows, add the `--flows` argument:

```json
{
  "mcpServers": {
    "agent-flows": {
      "command": "uvx",
      "args": [
        "agent-flows-mcp-server",
        "--flows",
        "uuid1,uuid2,uuid3"
      ],
      "env": {
        "AGENT_FLOWS_API_KEY": "your-api-key",
        "LITELLM_API_KEY": "your-llm-key",
        "LITELLM_API_BASE": "https://api.openai.com/v1",
        "MCP_ACI_API_KEY": "your-aci-key",
        "MCP_ACI_LINKED_ACCOUNT_OWNER_ID": "your-account-id"
      }
    }
  }
}
```

## How It Works

1. **Flow Discovery**: Server fetches all available flows from your RealTimeX instance
2. **Tool Generation**: Each flow becomes an MCP tool with:
   - Sanitized tool name (e.g., "Customer Onboarding Flow" → `customer_onboarding_flow`)
   - Flow description as tool description
   - Parameters extracted from the flow's START step variables
   - Structured output schema for success/failure cases
3. **Tool Execution**: When called, executes the corresponding flow with provided parameters
4. **Structured Results**: Returns JSON objects with execution details, not text

## Structured Output Format

### Success Response

```json
{
  "success": true,
  "flow_id": "uuid-123",
  "flow_name": "Customer Onboarding",
  "steps_executed": 5,
  "execution_time": 2.34,
  "started_at": "2025-01-13T09:15:00Z",
  "completed_at": "2025-01-13T09:15:02Z",
  "output": { "customer_id": "12345", "status": "active" },
  "variables": { "customer_name": "John Doe", "email": "john@example.com" },
  "direct_output": false,
  "errors": []
}
```

### Failure Response

```json
{
  "success": false,
  "flow_id": "uuid-123",
  "flow_name": "Customer Onboarding",
  "steps_executed": 3,
  "execution_time": 1.45,
  "started_at": "2025-01-13T09:15:00Z",
  "completed_at": "2025-01-13T09:15:01Z",
  "variables": { "customer_name": "John Doe" },
  "errors": [
    {
      "message": "Email validation failed",
      "step_id": "validate_email",
      "step_index": 2,
      "step_type": "validation",
      "error_type": "ValidationError",
      "timestamp": "2025-01-13T09:15:01Z"
    }
  ],
  "error_summary": "Flow execution failed with 1 error(s): step 'validate_email' (index 2) (validation) - ValidationError: Email validation failed"
}
```

## Configuration Options

### Required Environment Variables

- `AGENT_FLOWS_API_KEY`: Your RealTimeX API key
- `LITELLM_API_KEY`: API key for LLM provider
- `LITELLM_API_BASE`: Base URL for LLM API
- `MCP_ACI_API_KEY`: API key for ACI MCP integration
- `MCP_ACI_LINKED_ACCOUNT_OWNER_ID`: Linked account owner ID for ACI MCP

### Optional Configuration

- `AGENT_FLOWS_BASE_URL`: Your RealTimeX instance URL (default: "https://marketplace-api.realtimex.ai")
- `AGENT_FLOWS_TIMEOUT`: Request timeout in seconds (default: 30)
- `AGENT_FLOWS_CACHE_TTL`: Cache TTL in seconds (default: 3600)
- `MCP_SERVER_NAME`: Server name (default: "agent-flows-mcp")
- `MCP_TOOL_NAME_PREFIX`: Prefix for tool names (default: "")
- `SYSTEM_VARIABLES_API_URL`: Endpoint for retrieving system prompt variables (default: "http://localhost:3001/api/system/prompt-variables")

### System Variables

On each tool invocation, the server calls `http://localhost:3001/api/system/prompt-variables` with the MCP CLI's `AGENT_FLOWS_API_KEY` and header `X-App-Offline: true`. The endpoint responds with a payload in the form:

```json
{
  "variables": [
    {"key": "time", "type": "system", "value": "9:45:38 AM"},
    {"key": "user.email", "type": "user", "value": "user@example.com"}
  ]
}
```

The MCP server parses this structure into a flat dictionary (`{"time": "9:45:38 AM", ...}`) and merges it with the tool parameters for the current call. Because the values are fetched on demand, dynamic entries such as `time`, `date`, or `datetime` always reflect the latest data, and any updates made in the RealTimeX UI are picked up immediately. Tool arguments always take precedence over system variables when both define the same keys.

## Development

### Setup

```bash
git clone https://github.com/realtimex/agent-flows-mcp-server
cd agent-flows-mcp-server
pip install -e ".[dev]"
```

### Testing

```bash
pytest                    # Run all tests
pytest --cov            # Run with coverage
pytest -m integration   # Run integration tests
```

### Debug Mode

```bash
AGENT_FLOWS_API_KEY=your-key \
AGENT_FLOWS_BASE_URL=https://your-instance.com \
LITELLM_API_KEY=your-llm-key \
LITELLM_API_BASE=https://api.openai.com/v1 \
MCP_ACI_API_KEY=your-aci-key \
MCP_ACI_LINKED_ACCOUNT_OWNER_ID=your-account-id \
agent-flows-mcp-server --log-level DEBUG

# Or with specific flows only
AGENT_FLOWS_API_KEY=your-key \
AGENT_FLOWS_BASE_URL=https://your-instance.com \
LITELLM_API_KEY=your-llm-key \
LITELLM_API_BASE=https://api.openai.com/v1 \
MCP_ACI_API_KEY=your-aci-key \
MCP_ACI_LINKED_ACCOUNT_OWNER_ID=your-account-id \
agent-flows-mcp-server --flows "uuid1,uuid2,uuid3" --log-level DEBUG
```

## Integration

This MCP server leverages the [agent-flows](https://pypi.org/project/agent-flows/) package for all flow operations, providing a thin MCP wrapper around its robust execution engine.

## License

MIT License - see LICENSE file for details.
