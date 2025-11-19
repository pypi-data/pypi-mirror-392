"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest

from agent_flows_mcp.config import (
    MCPServerConfig,
    get_environment_info,
    get_mcp_server_config,
    get_session_id,
    load_mcp_config,
    validate_environment,
)


class TestMCPServerConfig:
    """Test MCP server configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MCPServerConfig()

        assert config.server_name == "agent-flows-mcp"
        assert config.server_version == "1.0.0"
        assert config.tool_name_prefix == ""
        assert config.max_tool_name_length == 64

    def test_config_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "MCP_SERVER_NAME": "custom-server",
                "MCP_SERVER_VERSION": "2.0.0",
                "MCP_TOOL_NAME_PREFIX": "test_",
                "MCP_MAX_TOOL_NAME_LENGTH": "32",
            },
        ):
            config = get_mcp_server_config()

            assert config.server_name == "custom-server"
            assert config.server_version == "2.0.0"
            assert config.tool_name_prefix == "test_"
            assert config.max_tool_name_length == 32


class TestLoadMCPConfig:
    """Test MCP configuration loading."""

    def test_load_config_success(self):
        """Test successful configuration loading."""
        with patch.dict(
            os.environ,
            {
                "AGENT_FLOWS_API_KEY": "test-key",
                "AGENT_FLOWS_BASE_URL": "https://test.com",
            },
        ):
            config = load_mcp_config()

            assert config.api_key == "test-key"
            assert config.base_url == "https://test.com"

    def test_load_config_missing_api_key(self):
        """Test configuration loading with missing API key."""
        with patch.dict(
            os.environ, {"AGENT_FLOWS_BASE_URL": "https://test.com"}, clear=True
        ):
            with pytest.raises(SystemExit):
                load_mcp_config()

    def test_load_config_missing_base_url(self):
        """Test configuration loading falls back to default base URL when missing."""
        with patch.dict(os.environ, {"AGENT_FLOWS_API_KEY": "test-key"}, clear=True):
            config = load_mcp_config()

            assert config.api_key == "test-key"
            assert config.base_url == "https://marketplace-api.realtimex.ai"


class TestValidateEnvironment:
    """Test environment validation."""

    def test_validate_environment_success(self):
        """Test successful environment validation."""
        with patch.dict(
            os.environ,
            {
                "AGENT_FLOWS_API_KEY": "test-key",
                "MCP_ACI_API_KEY": "aci-key",
                "MCP_ACI_LINKED_ACCOUNT_OWNER_ID": "owner-id",
                "LITELLM_API_KEY": "llm-key",
                "LITELLM_API_BASE": "https://api.example.com",
            },
        ):
            validate_environment()  # Should not raise

    def test_validate_environment_missing_api_key(self):
        """Test validation failure with missing API key."""
        with patch.dict(os.environ, {"MCP_ACI_API_KEY": "aci-key"}, clear=True):
            with pytest.raises(
                ValueError, match="Missing required environment variables"
            ):
                validate_environment()

    def test_validate_environment_missing_mcp_key(self):
        """Test validation failure with missing MCP ACI key."""
        with patch.dict(
            os.environ,
            {
                "AGENT_FLOWS_API_KEY": "test-key",
                "MCP_ACI_LINKED_ACCOUNT_OWNER_ID": "owner-id",
                "LITELLM_API_KEY": "llm-key",
                "LITELLM_API_BASE": "https://api.example.com",
            },
            clear=True,
        ):
            with pytest.raises(
                ValueError, match="Missing required environment variables"
            ):
                validate_environment()


class TestGetEnvironmentInfo:
    """Test environment information gathering."""

    def test_get_environment_info(self):
        """Test getting environment information."""
        with patch.dict(
            os.environ,
            {
                "AGENT_FLOWS_API_KEY": "test-key",
                "AGENT_FLOWS_BASE_URL": "https://test.com",
                "LITELLM_API_KEY": "llm-key",
                "MCP_SERVER_NAME": "custom-server",
            },
        ):
            info = get_environment_info()

            assert info["agent_flows_base_url"] == "https://test.com"
            assert info["agent_flows_api_key_set"] is True
            assert info["litellm_api_key_set"] is True
            assert info["mcp_server_name"] == "custom-server"

    def test_get_environment_info_minimal(self):
        """Test getting environment info with minimal setup."""
        with patch.dict(os.environ, {}, clear=True):
            info = get_environment_info()

            assert info["agent_flows_base_url"] == "Not set"
            assert info["agent_flows_api_key_set"] is False
            assert info["litellm_api_key_set"] is False
            assert info["mcp_server_name"] == "agent-flows-mcp"


class TestGetSessionId:
    """Test session ID retrieval."""

    def test_get_session_id_with_env_var(self):
        """Test getting session ID from environment variable."""
        with patch.dict(os.environ, {"SESSION_ID": "test-session-123"}):
            session_id = get_session_id()
            assert session_id == "test-session-123"

    def test_get_session_id_without_env_var(self):
        """Test getting session ID when environment variable is not set."""
        with patch.dict(os.environ, {}, clear=True):
            session_id = get_session_id()
            assert session_id is None
