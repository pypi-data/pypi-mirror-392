"""
Agent Flows MCP Server

A Model Context Protocol (MCP) server that dynamically provides tools based on
Agent Flows available in a user's RealTimeX instance.

This package provides a simplified, production-ready MCP server that leverages
the existing agent-flows package capabilities for maximum reliability and
minimal code duplication.
"""

__version__ = "1.0.0"
__author__ = "RealTimeX"
__email__ = "support@realtimex.com"

from .models import FlowExecutionFailure, FlowExecutionResult
from .server import AgentFlowsMCPServer

__all__ = [
    "AgentFlowsMCPServer",
    "FlowExecutionResult",
    "FlowExecutionFailure",
]
