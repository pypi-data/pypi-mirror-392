"""Tests for flow manager."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agent_flows.models.config import AgentFlowsConfig
from agent_flows.models.flow import FlowConfig, FlowStep

from agent_flows_mcp.flow_manager import FlowManager


@pytest.fixture
def mock_config():
    """Create a mock AgentFlowsConfig."""
    return AgentFlowsConfig(
        api_key="test-key",
        base_url="https://test.com",
        timeout=30,
        max_retries=3,
        cache_enabled=True,
        cache_ttl=3600,
        log_level="INFO",
    )


@pytest.fixture
def sample_flows():
    """Create sample flow configurations."""
    return [
        FlowConfig(
            uuid="550e8400-e29b-41d4-a716-446655440001",
            name="Test Flow 1",
            description="A test flow",
            steps=[
                FlowStep(
                    id="start-1",
                    type="flow_variables",
                    config={"variables": []},
                )
            ],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            status="active",
            tags=["test"],
        ),
        FlowConfig(
            uuid="550e8400-e29b-41d4-a716-446655440002",
            name="Test Flow 2",
            description="Another test flow",
            steps=[
                FlowStep(
                    id="start-1",
                    type="flow_variables",
                    config={"variables": []},
                )
            ],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            status="active",
            tags=["test"],
        ),
    ]


class TestFlowManager:
    """Test FlowManager functionality."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_config):
        """Test flow manager initialization."""
        flow_manager = FlowManager(mock_config)

        assert flow_manager.config == mock_config
        assert flow_manager.executor is None
        assert not flow_manager._initialized

    @pytest.mark.asyncio
    async def test_initialize_creates_executor(self, mock_config):
        """Test that initialize creates a FlowExecutor."""
        flow_manager = FlowManager(mock_config)

        with patch("agent_flows_mcp.flow_manager.FlowExecutor") as mock_executor_class:
            mock_executor = AsyncMock()
            mock_executor_class.return_value = mock_executor

            await flow_manager.initialize()

            assert flow_manager._initialized
            assert flow_manager.executor == mock_executor
            mock_executor_class.assert_called_once_with(
                config=mock_config, session_id=None
            )

    @pytest.mark.asyncio
    async def test_get_flows(self, mock_config, sample_flows):
        """Test getting flows."""
        flow_manager = FlowManager(mock_config)

        with patch("agent_flows_mcp.flow_manager.FlowExecutor") as mock_executor_class:
            mock_executor = AsyncMock()
            mock_executor.list_flows.return_value = sample_flows
            mock_executor_class.return_value = mock_executor

            flows = await flow_manager.get_flows()

            assert flows == sample_flows
            mock_executor.list_flows.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_flow(self, mock_config):
        """Test flow execution."""
        flow_manager = FlowManager(mock_config)

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.execution_time = 1.5

        with patch("agent_flows_mcp.flow_manager.FlowExecutor") as mock_executor_class:
            mock_executor = AsyncMock()
            mock_executor.execute_flow.return_value = mock_result
            mock_executor_class.return_value = mock_executor

            flow_id = "550e8400-e29b-41d4-a716-446655440003"
            result = await flow_manager.execute_flow(
                flow_id=flow_id, variables={"input": "test"}
            )

            assert result == mock_result
            mock_executor.execute_flow.assert_called_once_with(
                flow_source=flow_id, variables={"input": "test"}
            )

    @pytest.mark.asyncio
    async def test_close(self, mock_config):
        """Test closing the flow manager."""
        flow_manager = FlowManager(mock_config)

        with patch("agent_flows_mcp.flow_manager.FlowExecutor") as mock_executor_class:
            mock_executor = AsyncMock()
            mock_executor_class.return_value = mock_executor

            await flow_manager.initialize()
            await flow_manager.close()

            assert not flow_manager._initialized
            mock_executor.close.assert_called_once()
