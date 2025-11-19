"""
Agent-friendly MCP models for flow execution results.

These models provide a clean, structured interface optimized for AI agent consumption,
following the agent-first design principles outlined in the redesign documentation.
"""

from enum import Enum
from typing import Any, Literal

from agent_flows.models.execution import ExecutionError, FlowResult
from pydantic import BaseModel, Field


class FlowExecutionStatus(str, Enum):
    """High-level status of a flow execution."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class AgentFlowOutcomeType(str, Enum):
    """Enumeration of possible flow result types for agent consumption."""

    EXECUTION_COMPLETE = "EXECUTION_COMPLETE"
    EXECUTION_FAILED = "EXECUTION_FAILED"


class FlowOutcome(BaseModel):
    """Structured outcome information for agent consumption."""

    type: AgentFlowOutcomeType = Field(description="Type of flow execution outcome")
    summary: str = Field(description="Human-readable summary of the outcome")


class FlowErrorDetail(BaseModel):
    """Structured error information for programmatic inspection."""

    message: str = Field(description="Error message")
    step_id: str | None = Field(None, description="ID of the step where error occurred")
    step_type: str | None = Field(None, description="Type of step that failed")
    error_type: str | None = Field(None, description="Type of the original exception")


class FlowExecutionResult(BaseModel):
    """
    Agent-friendly model for successful flow execution results.

    Provides a clean, structured interface optimized for AI agent consumption
    with clear separation of outcome and output data.
    """

    status: Literal[FlowExecutionStatus.SUCCESS] = Field(
        FlowExecutionStatus.SUCCESS,
        description="The primary, high-level signal of the outcome.",
    )
    outcome: FlowOutcome = Field(
        description="A structured, descriptive summary of the result."
    )
    output: Any = Field(
        description="The machine-readable data payload. This is the primary data product of the tool."
    )
    ui_components: list[dict[str, Any]] | None = Field(
        None,
        description="UI component configuration derived from the flow definition.",
        serialization_alias="ui-components",
    )
    flow_as_output: bool = Field(
        False, description="Whether to use flow result as the output"
    )


class FlowExecutionFailure(BaseModel):
    """
    Agent-friendly model for failed flow execution results.

    Provides structured failure information with clear error details for debugging.
    """

    status: Literal[FlowExecutionStatus.FAILURE] = Field(
        FlowExecutionStatus.FAILURE,
        description="The primary, high-level signal of the outcome.",
    )
    outcome: FlowOutcome = Field(description="A structured summary of the failure.")
    output: Any = Field(None, description="Will always be `null` on failure.")
    ui_components: list[dict[str, Any]] | None = Field(
        None,
        description="UI component configuration derived from the flow definition.",
        serialization_alias="ui-components",
    )
    flow_as_output: bool = Field(
        False, description="Whether to use flow result as the output"
    )
    error_details: list[FlowErrorDetail] = Field(
        description="A structured list of curated error objects for deeper, programmatic inspection of the failure."
    )


class FlowResultMapper:
    """
    Maps internal FlowResult objects to agent-friendly models.

    This component handles the translation from verbose internal results
    to concise, structured models optimized for AI agent consumption.
    """

    @staticmethod
    def _generate_success_summary(flow_name: str) -> str:
        """Generate a deterministic success summary message."""
        return f"Flow '{flow_name}' completed successfully."

    @staticmethod
    def _generate_failure_summary(flow_result: FlowResult, flow_name: str) -> str:
        """Generate a deterministic failure summary message."""
        if not flow_result.errors:
            return f"Flow '{flow_name}' failed with no specific error details."

        # Use the first error for the primary summary
        primary_error = flow_result.errors[0]
        step_info = primary_error.get_step_identifier()

        summary = f"Flow '{flow_name}' failed: {step_info}"

        if primary_error.step_type:
            summary += f" ({primary_error.step_type})"

        summary += f": {primary_error.message}"

        return summary

    @staticmethod
    def _extract_output(flow_result: FlowResult) -> Any:
        """Extract the output data from FlowResult."""
        # The output comes from the result.data field as specified in the documentation
        return flow_result.result.data

    @staticmethod
    def _convert_errors_to_details(
        errors: list[ExecutionError],
    ) -> list[FlowErrorDetail]:
        """Convert ExecutionError objects to FlowErrorDetail objects."""
        return [
            FlowErrorDetail(
                message=error.message,
                step_id=error.step_id,
                step_type=error.step_type,
                error_type=error.error_type,
            )
            for error in errors
        ]

    @classmethod
    def to_success_result(
        cls, flow_result: FlowResult, flow_name: str
    ) -> FlowExecutionResult:
        """
        Convert a successful FlowResult to FlowExecutionResult.

        Args:
            flow_result: Successful FlowResult from agent-flows execution
            flow_name: Name of the flow that was executed

        Returns:
            FlowExecutionResult optimized for agent consumption
        """
        summary = cls._generate_success_summary(flow_name)
        output_data = cls._extract_output(flow_result)

        outcome = FlowOutcome(
            type=AgentFlowOutcomeType.EXECUTION_COMPLETE, summary=summary
        )

        return FlowExecutionResult(
            outcome=outcome,
            output=output_data,
            ui_components=flow_result.ui_components,
            flow_as_output=flow_result.flow_as_output,
        )

    @classmethod
    def to_failure_result(
        cls, flow_result: FlowResult, flow_name: str
    ) -> FlowExecutionFailure:
        """
        Convert a failed FlowResult to FlowExecutionFailure.

        Args:
            flow_result: Failed FlowResult from agent-flows execution
            flow_name: Name of the flow that was executed

        Returns:
            FlowExecutionFailure optimized for agent consumption
        """
        summary = cls._generate_failure_summary(flow_result, flow_name)
        error_details = cls._convert_errors_to_details(flow_result.errors)

        outcome = FlowOutcome(
            type=AgentFlowOutcomeType.EXECUTION_FAILED, summary=summary
        )

        return FlowExecutionFailure(
            outcome=outcome,
            output=None,
            ui_components=flow_result.ui_components,
            flow_as_output=flow_result.flow_as_output,
            error_details=error_details,
        )
