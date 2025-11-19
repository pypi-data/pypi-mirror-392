from __future__ import annotations

from types import SimpleNamespace

import httpx
import pytest

from agent_flows_mcp.config import MCPServerConfig
from agent_flows_mcp.server import AgentFlowsMCPServer
from agent_flows_mcp.system_variables import fetch_system_variables


@pytest.mark.asyncio
async def test_fetch_system_variables_success(mocker):
    response = mocker.Mock()
    response.status_code = httpx.codes.OK
    response.json.return_value = {
        "variables": [
            {"key": "time", "value": "9:45:38 AM", "type": "system"},
            {"key": "user.email", "value": "user@example.com", "type": "user"},
        ]
    }

    client = mocker.AsyncMock()
    client.get.return_value = response

    client_cm = mocker.AsyncMock()
    client_cm.__aenter__.return_value = client
    client_cm.__aexit__.return_value = False

    mocker.patch("httpx.AsyncClient", return_value=client_cm)

    variables = await fetch_system_variables("http://localhost/test", "token")

    assert variables == {
        "time": "9:45:38 AM",
        "user.email": "user@example.com",
    }
    client.get.assert_awaited_once_with(
        "http://localhost/test",
        headers={
            "Authorization": "Bearer token",
            "X-App-Offline": "true",
            "Accept": "application/json",
        },
    )


@pytest.mark.asyncio
async def test_fetch_system_variables_handles_errors(mocker):
    client = mocker.AsyncMock()
    client.get.side_effect = httpx.RequestError("boom")

    client_cm = mocker.AsyncMock()
    client_cm.__aenter__.return_value = client
    client_cm.__aexit__.return_value = False

    mocker.patch("httpx.AsyncClient", return_value=client_cm)

    variables = await fetch_system_variables("http://localhost/test", "token")

    assert variables == {}


@pytest.mark.asyncio
async def test_server_fetch_system_variables_every_call(mocker):
    mocker.patch("agent_flows_mcp.server.FlowManager")

    agent_flows_config = SimpleNamespace(api_key="key", base_url="", timeout=30)
    mcp_config = MCPServerConfig()

    server = AgentFlowsMCPServer(agent_flows_config, mcp_config)

    fetch_mock = mocker.AsyncMock(return_value={"user": {"id": 1}})
    mocker.patch("agent_flows_mcp.server.fetch_system_variables", fetch_mock)

    await server._fetch_system_variables()
    await server._fetch_system_variables()

    assert fetch_mock.await_count == 2


def test_merge_with_system_variables_merges_without_side_effects(mocker):
    mocker.patch("agent_flows_mcp.server.FlowManager")

    agent_flows_config = SimpleNamespace(api_key="key", base_url="", timeout=30)
    mcp_config = MCPServerConfig()

    server = AgentFlowsMCPServer(agent_flows_config, mcp_config)

    system_vars = {"user": {"id": 1}, "token": "abc"}
    params = {"user": {"name": "Ada"}}

    merged = server._merge_with_system_variables(system_vars, params)

    assert merged == {"user": {"id": 1, "name": "Ada"}, "token": "abc"}
    assert system_vars == {"user": {"id": 1}, "token": "abc"}
    assert params == {"user": {"name": "Ada"}}
