"""
CLI interface for Agent Flows MCP Server.

Handles command-line argument parsing and server startup logic.
"""

import asyncio
import sys

import click
import structlog
from agent_flows.utils.logging import setup_logging

from agent_flows_mcp.config import (
    get_mcp_server_config,
    load_mcp_config,
    validate_environment,
)
from agent_flows_mcp.server import AgentFlowsMCPServer

logger = structlog.get_logger(__name__)


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Logging level",
)
@click.option(
    "--flows",
    type=str,
    help="Comma-separated list of flow UUIDs to expose as tools (if not provided, all flows will be used)",
)
def main(log_level: str, flows: str | None) -> None:
    """Start the Agent Flows MCP Server."""
    try:
        # Configure logging
        setup_logging(level="DEBUG", json_format=True)

        # Parse flow UUIDs if provided
        flow_uuids = None
        if flows:
            flow_uuids = [uuid.strip() for uuid in flows.split(",") if uuid.strip()]
            logger.info(
                "Flow filtering enabled",
                flow_count=len(flow_uuids),
                flow_uuids=flow_uuids,
            )

        # Run the server
        asyncio.run(run_server(flow_uuids))

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error("Server failed to start", error=str(e))
        sys.exit(1)


async def run_server(flow_uuids: list[str] | None = None) -> None:
    """Run the MCP server with the given configuration."""
    # Validate environment
    validate_environment()

    # Load configurations
    agent_flows_config = load_mcp_config()
    mcp_server_config = get_mcp_server_config()

    # Create and start server
    server = AgentFlowsMCPServer(agent_flows_config, mcp_server_config, flow_uuids)
    await server.start()


if __name__ == "__main__":
    main()
