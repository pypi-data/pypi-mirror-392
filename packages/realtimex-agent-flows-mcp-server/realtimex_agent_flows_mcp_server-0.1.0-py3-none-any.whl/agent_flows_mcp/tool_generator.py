"""
Dynamic tool generation for Agent Flows MCP Server.

This module converts Agent Flows into MCP tools by analyzing flow configurations
and generating appropriate tool definitions with parameters.
"""

import json
import re
from typing import Any

import structlog
from agent_flows.models.flow import FlowConfig
from mcp.types import Tool
from pydantic import BaseModel

from .config import MCPServerConfig

logger = structlog.get_logger(__name__)


class ToolParameter(BaseModel):
    """Represents a tool parameter extracted from flow configuration."""

    name: str
    type: str
    description: str | None = None
    required: bool = True
    default: Any | None = None
    enum: list[str] | None = None


class GeneratedTool(BaseModel):
    """Represents a generated MCP tool."""

    name: str
    description: str
    flow_id: str
    flow_name: str
    parameters: list[ToolParameter]
    mcp_tool: Tool


class ToolGenerator:
    """
    Generates MCP tools from Agent Flow configurations.

    This class analyzes FlowConfig objects to create
    appropriate MCP tool definitions with parameters extracted from
    the flow's FLOW_VARIABLES step.
    """

    def __init__(self, mcp_config: MCPServerConfig):
        self.mcp_config = mcp_config
        self._generated_names: set[str] = set()

    def sanitize_tool_name(self, flow_name: str, flow_id: str) -> str:
        """
        Convert flow name to a valid MCP tool name.

        Args:
            flow_name: Original flow name
            flow_id: Flow UUID for uniqueness

        Returns:
            Sanitized tool name
        """
        # Convert to lowercase and replace spaces/special chars with underscores
        name = re.sub(r"[^a-zA-Z0-9_]", "_", flow_name.lower())

        # Remove multiple consecutive underscores
        name = re.sub(r"_+", "_", name)

        # Remove leading/trailing underscores
        name = name.strip("_")

        # Add prefix if configured
        if self.mcp_config.tool_name_prefix:
            name = f"{self.mcp_config.tool_name_prefix}_{name}"

        # Ensure it's not empty
        if not name:
            name = "flow_tool"

        # Truncate if too long (leave room for suffix)
        max_length = self.mcp_config.max_tool_name_length - 10
        if len(name) > max_length:
            name = name[:max_length]

        # Handle name collisions by appending flow ID suffix
        original_name = name
        counter = 1
        while name in self._generated_names:
            # Use first 8 chars of flow ID for uniqueness
            suffix = flow_id.replace("-", "")[:8]
            name = f"{original_name}_{suffix}"

            # If still too long, truncate the original name more
            if len(name) > self.mcp_config.max_tool_name_length:
                truncated = original_name[: max_length - len(suffix) - 1]
                name = f"{truncated}_{suffix}"

            counter += 1
            if counter > 10:  # Safety break
                break

        self._generated_names.add(name)
        return name

    def _coerce_default_value(
        self, value: Any, param_type: str, param_name: str, flow_id: str
    ) -> Any:
        """
        Intelligently coerce default values to match the specified parameter type.
        Logs a warning and returns None if coercion fails.
        """
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None

        original_value = value
        try:
            if param_type == "string":
                if isinstance(value, str):
                    return value
                if isinstance(value, int | float | bool):
                    return str(value)
                if not isinstance(value, str):
                    raise ValueError(f"Cannot convert {type(value).__name__} to string")
                return value

            elif param_type == "number":
                if isinstance(value, int | float):
                    return value
                if isinstance(value, str):
                    value = value.strip()
                    if "." in value or "e" in value.lower() or "E" in value:
                        return float(value)
                    return int(value)
                raise ValueError(f"Cannot convert {type(value).__name__} to number")

            elif param_type == "boolean":
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    v_lower = value.strip().lower()
                    if v_lower in {"true", "1", "yes", "y", "on", "t"}:
                        return True
                    if v_lower in {"false", "0", "no", "n", "off", "f"}:
                        return False
                if isinstance(value, int | float):
                    if value == 1:
                        return True
                    if value == 0:
                        return False
                raise ValueError(f"Cannot convert '{value}' to boolean")

            elif param_type == "array":
                if isinstance(value, list):
                    return value
                if isinstance(value, str):
                    parsed = json.loads(value.strip())
                    if isinstance(parsed, list):
                        return parsed
                raise ValueError(f"Cannot convert {type(value).__name__} to array")

            elif param_type == "object":
                if isinstance(value, dict):
                    return value
                if isinstance(value, str):
                    parsed = json.loads(value.strip())
                    if isinstance(parsed, dict):
                        return parsed
                raise ValueError(f"Cannot convert {type(value).__name__} to object")

            return value
        except (ValueError, json.JSONDecodeError) as e:
            logger.warning(
                "Failed to coerce default value for parameter",
                param_name=param_name,
                param_type=param_type,
                default_value=original_value,
                flow_id=flow_id,
                error=str(e),
            )
            return None

    def extract_parameters_from_variables_step(
        self, flow_config: FlowConfig
    ) -> list[ToolParameter]:
        """
        Extract parameters from the flow's FLOW_VARIABLES node.

        Based on the current FLOW_VARIABLES step specification, variables are defined as:
        - Array format only: [{"name": "var1", "type": "string", "value": "default", "description": "...", "source": "user_input"}]
        - Variables with "source": "node_output" are excluded from tool parameters (runtime variables)
        - Variables with "source": "system" are excluded from tool parameters (system configuration)
        - Variables with "source": "user_input" or missing field are included as tool parameters
        - Uses "value" field for default values

        Args:
            flow_config: Flow configuration

        Returns:
            List of tool parameters (only variables with source 'user_input')
        """
        parameters = []

        # Find the FLOW_VARIABLES step
        step_config = None
        for step in flow_config.steps:
            if step.type.lower() == "flow_variables":
                step_config = step
                break

        if not step_config or not step_config.config:
            logger.debug(
                "No FLOW_VARIABLES step or config found",
                flow_id=flow_config.uuid,
                flow_name=flow_config.name,
            )
            return parameters

        # Extract variables from FLOW_VARIABLES step config - only array format is supported
        variables = step_config.config.get("variables", [])

        # Only handle array format as per new specification
        if isinstance(variables, list):
            for var_def in variables:
                if isinstance(var_def, dict) and "name" in var_def:
                    # Check variable source - only include user_input variables
                    # Default to "user_input" if not specified for backward compatibility
                    source = var_def.get("source", "user_input")

                    if source != "user_input":
                        logger.debug(
                            "Skipping variable - not user input",
                            flow_id=flow_config.uuid,
                            variable_name=var_def["name"],
                            source=source,
                        )
                        continue

                    param_name = var_def["name"]
                    param_type = self._map_variable_type(var_def.get("type", "string"))
                    description = (
                        var_def.get("description") or f"Flow variable: {param_name}"
                    )
                    # All variables are optional since they have initial values
                    required = False
                    # Use "value" field as per new specification
                    default_value = var_def.get("value")
                    enum_values = var_def.get("enum")

                    # Coerce default value to match parameter type
                    coerced_default = self._coerce_default_value(
                        default_value, param_type, param_name, flow_config.uuid
                    )

                    parameters.append(
                        ToolParameter(
                            name=param_name,
                            type=param_type,
                            description=description,
                            required=required,
                            default=coerced_default,
                            enum=enum_values,
                        )
                    )
        else:
            # Log warning for unsupported format
            logger.warning(
                "Unsupported variables format in FLOW_VARIABLES step - only array format is supported",
                flow_id=flow_config.uuid,
                flow_name=flow_config.name,
                variables_type=type(variables).__name__,
            )

        logger.debug(
            "Extracted parameters from FLOW_VARIABLES step",
            flow_id=flow_config.uuid,
            parameter_count=len(parameters),
            parameter_names=[p.name for p in parameters],
        )

        return parameters

    def _map_variable_type(self, var_type: str) -> str:
        """
        Map flow variable types to JSON Schema types.

        Args:
            var_type: Flow variable type

        Returns:
            JSON Schema type
        """
        type_mapping = {
            "string": "string",
            "text": "string",
            "number": "number",
            "integer": "integer",
            "int": "integer",
            "boolean": "boolean",
            "bool": "boolean",
            "array": "array",
            "list": "array",
            "object": "object",
            "dict": "object",
        }

        return type_mapping.get(var_type.lower(), "string")

    def _infer_array_item_type(self, array_value: list) -> str:
        """
        Infer the item type for an array based on its values.

        Args:
            array_value: Array value to analyze

        Returns:
            JSON Schema type for array items
        """
        if not array_value:
            return "string"  # Default to string for empty arrays

        # Get the type of the first non-null item
        for item in array_value:
            if item is not None:
                if isinstance(item, str):
                    return "string"
                elif isinstance(item, bool):
                    return "boolean"
                elif isinstance(item, int):
                    return "integer"
                elif isinstance(item, float):
                    return "number"
                elif isinstance(item, dict):
                    return "object"
                elif isinstance(item, list):
                    return "array"

        return "string"  # Default fallback

    def is_return_direct(
        self, flow_config: FlowConfig
    ) -> list[ToolParameter]:
        """
        Find flow is return direct or not

        Args:
            flow_config: Flow configuration

        Returns:
            True or Flase
        """
        for step in flow_config.steps:
            if step.type.lower() == "finish":
                return step.config.get("flowAsOutput", False)
        return False

    def create_input_schema(self, parameters: list[ToolParameter]) -> dict[str, Any]:
        """
        Create JSON Schema for tool input parameters.

        Args:
            parameters: List of tool parameters

        Returns:
            JSON Schema dictionary for input
        """
        if not parameters:
            return {"type": "object", "properties": {}, "required": []}

        properties = {}
        required = []

        for param in parameters:
            prop_schema = {"type": param.type}

            if param.description:
                prop_schema["description"] = param.description

            if param.enum:
                prop_schema["enum"] = param.enum

            # Handle array types with items schema
            if param.type == "array" and param.default is not None:
                if isinstance(param.default, list):
                    # Infer item type from the default array values
                    item_type = self._infer_array_item_type(param.default)
                    prop_schema["items"] = {"type": item_type}
                else:
                    # Fallback to string items if default is not a list
                    prop_schema["items"] = {"type": "string"}

            if param.default is not None:
                prop_schema["default"] = param.default

            properties[param.name] = prop_schema

            if param.required:
                required.append(param.name)

        return {"type": "object", "properties": properties, "required": required}

    def create_output_schema(self) -> dict[str, Any]:
        """
        Create JSON Schema for tool output.

        Returns a schema that matches the new agent-friendly data contract,
        covering both successful and failed executions.

        Returns:
            JSON Schema dictionary for output
        """
        return {
            "type": "object",
            "description": "Represents the outcome of a tool execution. The structure depends on the 'status' field.",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["SUCCESS", "FAILURE"],
                    "description": "The primary, high-level signal of the outcome.",
                },
                "outcome": {
                    "type": "object",
                    "description": "A structured, descriptive summary of the result.",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["EXECUTION_COMPLETE", "EXECUTION_FAILED"],
                            "description": "An agent-friendly enum describing the outcome type.",
                        },
                        "summary": {
                            "type": "string",
                            "description": "A simple, human-readable message summarizing the outcome.",
                        },
                    },
                    "required": ["type", "summary"],
                },
                "output": {
                    "description": "The machine-readable data payload. This is the primary data product of the tool. It will be `null` on failure."
                },
                "ui-components": {
                    "type": ["array", "null"],
                    "description": "UI component configuration derived from the flow definition.",
                    "items": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": "Single UI component definition.",
                    },
                },
                "flow_as_output": {
                    "type": "boolean",
                    "description": "Indicates if the flow definition was returned as part of the output.",
                    "default": False,
                },
                "error_details": {
                    "type": "array",
                    "description": "A structured list of curated error objects for deeper, programmatic inspection of the failure. Only present on failure",
                    "items": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Error message",
                            },
                            "step_id": {
                                "type": ["string", "null"],
                                "description": "ID of the step where error occurred",
                            },
                            "step_type": {
                                "type": ["string", "null"],
                                "description": "Type of step that failed",
                            },
                            "error_type": {
                                "type": ["string", "null"],
                                "description": "Type of the original exception",
                            },
                        },
                        "required": ["message"],
                    },
                },
            },
            "required": ["status", "outcome", "output"],
            # Use conditional schemas based on the 'status' field
            "if": {"properties": {"status": {"const": "FAILURE"}}},
            "then": {
                "properties": {
                    "output": {"type": "null"},
                    "outcome": {"properties": {"type": {"const": "EXECUTION_FAILED"}}},
                },
                "required": [
                    "status",
                    "outcome",
                    "output",
                    "error_details",
                ],
            },
            "else": {
                "properties": {
                    "outcome": {
                        "properties": {"type": {"const": "EXECUTION_COMPLETE"}}
                    },
                },
                "required": ["status", "outcome", "output"],
            },
        }

    def generate_tool_from_flow(self, flow_config: FlowConfig) -> GeneratedTool:
        """
        Generate an MCP tool from a flow summary and optional config.

        Args:
            flow_config: Flow configuration information

        Returns:
            Generated MCP tool
        """
        # Generate tool name
        tool_name = self.sanitize_tool_name(flow_config.name, flow_config.uuid)

        # Generate description
        description = (
            flow_config.description or f"Execute the '{flow_config.name}' flow"
        )

        # Mark return_direct
        return_direct = self.is_return_direct(flow_config)
        if return_direct:
            description = f"{description}@@__return_direct__@@"

        # Extract parameters
        parameters = self.extract_parameters_from_variables_step(flow_config)

        # Create input and output schemas
        input_schema = self.create_input_schema(parameters)
        output_schema = self.create_output_schema()

        # Create MCP tool with both input and output schemas
        mcp_tool = Tool(
            name=tool_name,
            description=description,
            inputSchema=input_schema,
            outputSchema=output_schema,
        )

        generated_tool = GeneratedTool(
            name=tool_name,
            description=description,
            flow_id=flow_config.uuid,
            flow_name=flow_config.name,
            parameters=parameters,
            mcp_tool=mcp_tool,
        )

        logger.debug(
            "Generated tool from flow",
            tool_name=tool_name,
            flow_id=flow_config.uuid,
            flow_name=flow_config.name,
            parameter_count=len(parameters),
        )

        return generated_tool

    def validate_tool_parameters(
        self, tool_name: str, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate and sanitize tool parameters before execution.

        Args:
            tool_name: Name of the tool being executed
            parameters: Parameters provided by the client

        Returns:
            Validated and sanitized parameters

        Raises:
            ValueError: If parameters are invalid
        """
        # Basic validation - ensure parameters is a dict
        if not isinstance(parameters, dict):
            raise ValueError(f"Parameters must be a dictionary, got {type(parameters)}")

        # Remove any None values
        cleaned_params = {k: v for k, v in parameters.items() if v is not None}

        logger.debug(
            "Validated tool parameters",
            tool_name=tool_name,
            original_count=len(parameters),
            cleaned_count=len(cleaned_params),
        )

        return cleaned_params

    def clear_generated_names(self) -> None:
        """Clear the set of generated names for a new batch."""
        self._generated_names.clear()

    def get_generation_stats(self) -> dict[str, Any]:
        """Get statistics about tool generation."""
        return {
            "generated_names_count": len(self._generated_names),
            "tool_name_prefix": self.mcp_config.tool_name_prefix,
            "max_tool_name_length": self.mcp_config.max_tool_name_length,
        }
