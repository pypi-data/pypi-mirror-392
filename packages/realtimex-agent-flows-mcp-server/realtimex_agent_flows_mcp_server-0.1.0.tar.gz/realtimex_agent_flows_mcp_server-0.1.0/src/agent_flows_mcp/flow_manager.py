"""
Simplified Flow Manager for Agent Flows MCP Server.

This module provides a thin wrapper around FlowExecutor, leveraging its
built-in caching and API client capabilities.
"""

import structlog
from agent_flows import FlowExecutor
from agent_flows.models.config import AgentFlowsConfig
from agent_flows.models.flow import FlowConfig

logger = structlog.get_logger(__name__)


class FlowManager:
    """
    Simplified flow manager that leverages FlowExecutor's built-in capabilities.

    This class is a thin wrapper around FlowExecutor, using its built-in
    caching, API client, and flow management features.
    """

    def __init__(
        self,
        config: AgentFlowsConfig,
        allowed_flow_uuids: list[str] | None = None,
        session_id: str | None = None,
        workspace_slug: str | None = None,
        thread_id: str | None = None
    ):
        self.config = config
        self.allowed_flow_uuids = allowed_flow_uuids
        self.session_id = session_id
        self.workspace_slug = workspace_slug
        self.thread_id = thread_id
        self.executor: FlowExecutor | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the flow manager and executor."""
        if self._initialized:
            return

        try:
            logger.info("Initializing FlowManager")

            # Create FlowExecutor - it handles all caching and API communication
            self.executor = FlowExecutor(config=self.config, session_id=self.session_id, thread_id=self.thread_id, workspace_slug=self.workspace_slug)

            self._initialized = True
            logger.info("FlowManager initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize FlowManager", error=str(e))
            raise

    async def close(self) -> None:
        """Clean up resources."""
        if self.executor:
            try:
                await self.executor.close()
                logger.info("FlowExecutor closed successfully")
            except Exception as e:
                logger.warning("Error closing FlowExecutor", error=str(e))

        self._initialized = False

    async def get_flows(self, force_refresh: bool = False) -> list[FlowConfig]:
        """
        Get all available flows using FlowExecutor's built-in caching.

        Args:
            force_refresh: Force refresh from RealTimeX (bypasses cache)

        Returns:
            List of available flows
        """
        if not self._initialized:
            await self.initialize()

        if not self.executor:
            raise RuntimeError("FlowManager not initialized")

        try:
            logger.debug("Fetching flows", force_refresh=force_refresh)

            # FlowExecutor.list_flows() handles caching automatically
            # We can bypass cache by invalidating it first if needed
            api_client = getattr(self.executor, "api_client", None)
            if force_refresh and api_client and hasattr(api_client, "invalidate_cache"):
                await api_client.invalidate_cache()

            flows = await self.executor.list_flows()

            # Filter flows if allowed_flow_uuids is specified
            if self.allowed_flow_uuids is not None:
                original_count = len(flows)
                flows = [flow for flow in flows if flow.uuid in self.allowed_flow_uuids]

                logger.info(
                    f"Filtered flows based on allowed list: {len(flows)} of {original_count} flows kept",
                    allowed_flow_names=[flow.name for flow in flows],
                )

            logger.info(
                "Flows retrieved successfully",
                count=len(flows),
                flow_names=[flow.name for flow in flows[:5]],  # Log first 5 names
            )

            return flows

        except Exception as e:
            logger.error("Failed to get flows", error=str(e))
            raise

    async def get_flow(self, flow_id: str) -> FlowConfig | None:
        """
        Get a specific flow by ID.

        Args:
            flow_id: UUID of the flow

        Returns:
            Flow configuration if found, None otherwise
        """
        flows = await self.get_flows()
        return next((flow for flow in flows if flow.uuid == flow_id), None)

    async def execute_flow(self, flow_id: str, variables: dict | None = None):
        """
        Execute a flow using FlowExecutor.

        Args:
            flow_id: UUID of the flow to execute
            variables: Flow variables

        Returns:
            FlowResult from the execution
        """
        if not self._initialized:
            await self.initialize()

        if not self.executor:
            raise RuntimeError("FlowManager not initialized")

        try:
            logger.info("Executing flow", flow_id=flow_id, variables=variables)

            result = await self.executor.execute_flow(
                flow_source=flow_id, variables=variables or {}
            )

            logger.info(
                "Flow execution completed",
                flow_id=flow_id,
                success=result.success,
                execution_time=result.execution_time,
            )

            return result

        except Exception as e:
            logger.error("Flow execution failed", flow_id=flow_id, error=str(e))
            raise
