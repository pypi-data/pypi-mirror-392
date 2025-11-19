"""
Configuration management for Agent Flows MCP Server.

Simplified configuration that leverages the existing agent-flows package
configuration system with minimal MCP-specific additions.
"""

import os

import structlog
from agent_flows.models.config import AgentFlowsConfig, LoggingConfig
from agent_flows.utils.config import load_config
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class MCPServerConfig(BaseModel):
    """Minimal MCP server specific configuration."""

    server_name: str = Field(default="agent-flows-mcp", description="MCP server name")
    server_version: str = Field(default="1.0.0", description="MCP server version")
    tool_name_prefix: str = Field(
        default="", description="Prefix for generated tool names"
    )
    max_tool_name_length: int = Field(
        default=64, description="Maximum tool name length"
    )
    system_variables_api_url: str = Field(
        default="http://localhost:3001/api/system/prompt-variables",
        description="Endpoint for retrieving system variables",
    )


def load_mcp_config(require_api_key: bool = True) -> AgentFlowsConfig:
    """
    Load configuration for the MCP server.

    Uses the existing agent-flows configuration system, which loads from
    environment variables.

    Args:
        require_api_key: If True, validates that AGENT_FLOWS_API_KEY is set.

    Returns:
        AgentFlowsConfig with all necessary settings.

    Raises:
        ValueError: If the required API key is missing.
    """
    logger.info("Loading MCP server configuration")
    try:
        # The agent_flows.load_config() function handles loading from env vars
        config = load_config()

        if require_api_key and not config.api_key:
            raise ValueError("AGENT_FLOWS_API_KEY environment variable must be set.")

        # Temporarily turn on debug logging for MCP server operations
        config.logging = LoggingConfig(level="DEBUG", json_format=True)

        logger.info(
            "Configuration loaded successfully",
            base_url=config.base_url,
            cache_enabled=config.cache_enabled,
            cache_ttl=config.cache_ttl,
        )
        return config
    except Exception as e:
        logger.error("Failed to load configuration", error=str(e))
        raise


def get_mcp_server_config() -> MCPServerConfig:
    """Get MCP server specific configuration from environment."""
    return MCPServerConfig(
        server_name=os.getenv("MCP_SERVER_NAME", "agent-flows-mcp"),
        server_version=os.getenv("MCP_SERVER_VERSION", "1.0.0"),
        tool_name_prefix=os.getenv("MCP_TOOL_NAME_PREFIX", ""),
        max_tool_name_length=int(os.getenv("MCP_MAX_TOOL_NAME_LENGTH", "64")),
        system_variables_api_url=os.getenv(
            "SYSTEM_VARIABLES_API_URL",
            "http://localhost:3001/api/system/prompt-variables",
        ),
    )


def get_session_id() -> str | None:
    """Get session ID from environment variable."""
    return os.getenv("SESSION_ID")

def get_thread_id() -> str | None:
    """Get thread ID from environment variable."""
    return os.getenv("THREAD_ID")

def get_workspace_slug() -> str | None:
    """Get workspace slug from environment variable."""
    return os.getenv("WORKSPACE_SLUG")

def validate_environment() -> None:
    """
    Validate that required environment variables are set.

    Raises:
        ValueError: If required environment variables are missing
    """
    required_vars = [
        "AGENT_FLOWS_API_KEY",
        "MCP_ACI_API_KEY",
        "MCP_ACI_LINKED_ACCOUNT_OWNER_ID",
        "LITELLM_API_KEY",
        "LITELLM_API_BASE",
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    logger.info("Environment validation passed")


def get_environment_info() -> dict:
    """
    Get information about the current environment configuration.

    Returns:
        Dictionary with environment information (without sensitive data)
    """
    return {
        "agent_flows_base_url": os.getenv("AGENT_FLOWS_BASE_URL", "Not set"),
        "agent_flows_api_key_set": bool(os.getenv("AGENT_FLOWS_API_KEY")),
        "litellm_api_key_set": bool(os.getenv("LITELLM_API_KEY")),
        "litellm_api_base": os.getenv("LITELLM_API_BASE", "Not set"),
        "mcp_aci_api_key_set": bool(os.getenv("MCP_ACI_API_KEY")),
        "mcp_server_name": os.getenv("MCP_SERVER_NAME", "agent-flows-mcp"),
        "system_variables_api_url": os.getenv(
            "SYSTEM_VARIABLES_API_URL",
            "http://localhost:3001/api/system/prompt-variables",
        ),
    }
