"""
Main MCP server implementation for Agent Flows.

Simplified implementation that leverages the existing agent-flows package
capabilities with minimal additional complexity.
"""

from __future__ import annotations

import copy
from typing import Any

import mcp.types as types
import structlog
from agent_flows.utils.dict_utils import deep_update
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import get_session_id, get_thread_id, get_workspace_slug
from .flow_manager import FlowManager
from .models import FlowResultMapper
from .system_variables import (
    DEFAULT_SYSTEM_VARIABLES_API_URL,
    fetch_system_variables,
)
from .tool_generator import GeneratedTool, ToolGenerator

logger = structlog.get_logger(__name__)


class AgentFlowsMCPServer:
    """
    Simplified MCP Server for Agent Flows.

    This server dynamically generates MCP tools based on flows available
    in a user's RealTimeX instance and handles tool execution.
    """

    def __init__(
        self,
        agent_flows_config,
        mcp_server_config,
        allowed_flow_uuids: list[str] | None = None,
    ):
        self.agent_flows_config = agent_flows_config
        self.mcp_server_config = mcp_server_config
        self.allowed_flow_uuids = allowed_flow_uuids
        self.server = Server(
            name=mcp_server_config.server_name,
            version=mcp_server_config.server_version,
        )
        self.flow_manager = FlowManager(
            agent_flows_config,
            allowed_flow_uuids,
            session_id=get_session_id(),
            workspace_slug=get_workspace_slug(),
            thread_id=get_thread_id()
        )
        self.tool_generator = ToolGenerator(mcp_server_config)
        self.generated_tools: dict[str, GeneratedTool] = {}
        self._initialized = False
        self._tools_loaded = False

        # Register MCP handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """Handle list_tools requests by returning pre-loaded tools."""
            try:
                logger.info("Received list_tools request")

                # Ensure tools are loaded (should already be loaded during startup)
                if not self._tools_loaded:
                    logger.warning("Tools not loaded during startup, loading now")
                    await self._load_tools()

                # Return pre-loaded tools
                tools = [tool.mcp_tool for tool in self.generated_tools.values()]

                logger.info(
                    "Returning pre-loaded tools for list_tools",
                    generated_tools=len(tools),
                )

                return tools

            except Exception as e:
                logger.error("Error in list_tools handler", error=str(e))
                # Return empty list on error to avoid breaking MCP protocol
                return []

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
            """Handle call_tool requests by executing the corresponding flow."""
            logger.info(
                "Received call_tool request",
                tool_name=name,
                arguments=arguments,
            )

            try:
                # Ensure server is initialized
                await self._ensure_initialized()

                # Find the generated tool
                generated_tool = self.generated_tools.get(name)
                if not generated_tool:
                    error_msg = f"Tool '{name}' not found. Available tools: {list(self.generated_tools.keys())}"
                    logger.error(
                        "Tool not found",
                        tool_name=name,
                        available_tools=list(self.generated_tools.keys()),
                    )
                    raise ValueError(error_msg)

                # Validate and prepare parameters
                try:
                    parameters = self.tool_generator.validate_tool_parameters(
                        name, arguments or {}
                    )
                except ValueError as e:
                    error_msg = f"Invalid parameters for tool '{name}': {str(e)}"
                    logger.error(
                        "Parameter validation failed", tool_name=name, error=str(e)
                    )
                    raise ValueError(error_msg) from e

                # Execute the flow using FlowManager (which uses FlowExecutor directly)
                try:
                    system_variables = await self._fetch_system_variables()
                    merged_parameters = self._merge_with_system_variables(
                        system_variables, parameters
                    )
                    result = await self.flow_manager.execute_flow(
                        flow_id=generated_tool.flow_id, variables=merged_parameters
                    )

                    logger.info(
                        "Tool execution completed",
                        tool_name=name,
                        flow_id=generated_tool.flow_id,
                        success=result.success,
                        execution_time=result.execution_time,
                    )

                    # Create agent-friendly result using the mapper
                    if result.success:
                        agent_result = FlowResultMapper.to_success_result(
                            flow_result=result, flow_name=generated_tool.flow_name
                        )
                        # Convert Pydantic model to dict for MCP
                        return agent_result.model_dump(mode="json", by_alias=True)
                    else:
                        agent_result = FlowResultMapper.to_failure_result(
                            flow_result=result, flow_name=generated_tool.flow_name
                        )
                        # Convert Pydantic model to dict for MCP
                        return agent_result.model_dump(mode="json", by_alias=True)

                except Exception as e:
                    error_msg = f"Flow execution failed for '{generated_tool.flow_name}' (ID: {generated_tool.flow_id}): {str(e)}"
                    logger.error(
                        "Flow execution exception",
                        tool_name=name,
                        flow_id=generated_tool.flow_id,
                        flow_name=generated_tool.flow_name,
                        error=str(e),
                        error_type=type(e).__name__,
                    )
                    raise RuntimeError(error_msg) from e

            except ValueError:
                # Re-raise ValueError for parameter/tool validation errors
                raise
            except Exception as e:
                # Wrap unexpected errors
                error_msg = (
                    f"Internal server error while executing tool '{name}': {str(e)}"
                )
                logger.error(
                    "Unexpected error in call_tool handler",
                    tool_name=name,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise RuntimeError(error_msg) from e

    async def _ensure_initialized(self) -> None:
        """Ensure the server is properly initialized."""
        if not self._initialized:
            await self.flow_manager.initialize()
            self._initialized = True

    async def _fetch_system_variables(self) -> dict[str, Any]:
        """Fetch the latest system variables from the configured endpoint."""

        api_url = (
            self.mcp_server_config.system_variables_api_url
            or DEFAULT_SYSTEM_VARIABLES_API_URL
        )
        system_variables = await fetch_system_variables(
            api_url=api_url,
            auth_token=self.agent_flows_config.api_key,
        )

        if system_variables:
            logger.debug(
                "System variables fetched",
                variable_count=len(system_variables),
                api_url=api_url,
            )
        else:
            logger.debug("No system variables fetched", api_url=api_url)

        return system_variables

    @staticmethod
    def _merge_with_system_variables(
        system_variables: dict[str, Any], parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge system variables with request parameters without mutating inputs."""

        if not system_variables:
            return copy.deepcopy(parameters) if parameters else {}

        merged_parameters: dict[str, Any] = copy.deepcopy(system_variables)

        if parameters:
            deep_update(merged_parameters, copy.deepcopy(parameters))

        return merged_parameters

    async def _load_tools(self) -> None:
        """Load and generate tools from available flows during startup."""
        if self._tools_loaded:
            return

        try:
            logger.info("Loading tools from available flows")

            # Ensure flow manager is initialized
            await self._ensure_initialized()

            # Get available flows
            flows = await self.flow_manager.get_flows()

            # Clear previous tools and generated names
            self.generated_tools.clear()
            self.tool_generator.clear_generated_names()

            # Generate tools from flows
            tools_count = 0
            for flow in flows:
                try:
                    # Generate tool directly from the flow configuration
                    generated_tool = self.tool_generator.generate_tool_from_flow(flow)

                    # Store for execution lookup
                    self.generated_tools[generated_tool.name] = generated_tool
                    tools_count += 1

                except Exception as e:
                    logger.warning(
                        "Failed to generate tool for flow during startup",
                        flow_id=flow.uuid,
                        flow_name=flow.name,
                        error=str(e),
                    )
                    continue

            self._tools_loaded = True
            logger.info(
                "Tools loaded successfully during startup",
                total_flows=len(flows),
                generated_tools=tools_count,
            )

        except Exception as e:
            logger.error("Failed to load tools during startup", error=str(e))
            raise RuntimeError(f"Tool loading failed: {str(e)}") from e

    async def start(self) -> None:
        """Start the MCP server."""
        try:
            logger.info(
                "Starting Agent Flows MCP Server",
                server_name=self.mcp_server_config.server_name,
                base_url=self.agent_flows_config.base_url,
                flow_filtering_enabled=self.allowed_flow_uuids is not None,
                allowed_flow_count=len(self.allowed_flow_uuids)
                if self.allowed_flow_uuids
                else None,
            )

            # Initialize components and load tools during startup
            await self._ensure_initialized()

            # Load tools - if this fails, the server startup should fail
            await self._load_tools()

            # Start STDIO server
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP server started successfully")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )

        except Exception as e:
            logger.error("Failed to start MCP server", error=str(e))
            raise
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Clean up server resources."""
        try:
            logger.info("Cleaning up MCP server resources")
            await self.flow_manager.close()
            logger.info("MCP server cleanup completed")
        except Exception as e:
            logger.warning("Error during cleanup", error=str(e))
