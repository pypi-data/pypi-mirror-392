"""Tests for tool generator."""

import pytest
from agent_flows.models.flow import FlowConfig
from mcp.types import Tool

from agent_flows_mcp.config import MCPServerConfig
from agent_flows_mcp.tool_generator import ToolGenerator, ToolParameter


@pytest.fixture
def mcp_config():
    """Create MCP server configuration."""
    return MCPServerConfig(
        server_name="test-server",
        server_version="1.0.0",
        tool_name_prefix="test",
        max_tool_name_length=64,
    )


@pytest.fixture
def sample_flow_config():
    """Create a sample flow configuration with FLOW_VARIABLES step using new specification."""
    return FlowConfig(
        uuid="550e8400-e29b-41d4-a716-446655440000",
        name="Customer Onboarding Flow",
        description="Automated customer onboarding process",
        steps=[
            {
                "id": "start-1",
                "type": "flow_variables",
                "config": {
                    "variables": [
                        {
                            "name": "customer_name",
                            "type": "string",
                            "value": "",
                            "description": "Customer's full name",
                        },
                        {
                            "name": "email",
                            "type": "string",
                            "value": "",
                            "description": "Customer's email address",
                        },
                        {
                            "name": "company",
                            "type": "string",
                            "value": "Default Corp",
                            "description": "Customer's company name",
                        },
                    ]
                },
            }
        ],
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        status="active",
        tags=["onboarding"],
    )


@pytest.fixture
def legacy_flow_config():
    """Create a legacy flow configuration that still uses the START step."""
    return FlowConfig(
        uuid="550e8400-e29b-41d4-a716-446655440000",
        name="Customer Onboarding Flow",
        description="Automated customer onboarding process",
        steps=[
            {
                "id": "start-legacy",
                "type": "start",
                "config": {
                    "variables": [
                        {
                            "name": "customer_id",
                            "type": "string",
                            "value": "",
                            "description": "Customer identifier",
                        }
                    ]
                },
            }
        ],
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        status="active",
        tags=["onboarding"],
    )


class TestToolGenerator:
    """Test ToolGenerator functionality."""

    def test_initialization(self, mcp_config):
        """Test tool generator initialization."""
        generator = ToolGenerator(mcp_config)

        assert generator.mcp_config == mcp_config
        assert len(generator._generated_names) == 0

    def test_sanitize_tool_name_basic(self, mcp_config):
        """Test basic tool name sanitization."""
        generator = ToolGenerator(mcp_config)

        result = generator.sanitize_tool_name("Customer Onboarding Flow", "flow-123")

        assert result == "test_customer_onboarding_flow"
        assert result in generator._generated_names

    def test_sanitize_tool_name_special_chars(self, mcp_config):
        """Test tool name sanitization with special characters."""
        generator = ToolGenerator(mcp_config)

        result = generator.sanitize_tool_name("Flow-Name@#$%^&*()", "flow-123")

        assert result == "test_flow_name"

    def test_sanitize_tool_name_collision(self, mcp_config):
        """Test tool name collision handling."""
        generator = ToolGenerator(mcp_config)

        # Generate first tool
        name1 = generator.sanitize_tool_name("Test Flow", "flow-123")

        # Generate second tool with same name
        name2 = generator.sanitize_tool_name("Test Flow", "flow-456")

        assert name1 == "test_test_flow"
        assert name2 == "test_test_flow_flow456"  # Should have suffix
        assert name1 != name2

    def test_extract_parameters_from_flow_variables_step(
        self, mcp_config, sample_flow_config
    ):
        """Test parameter extraction from FLOW_VARIABLES step."""
        generator = ToolGenerator(mcp_config)

        parameters = generator.extract_parameters_from_variables_step(
            sample_flow_config
        )

        assert len(parameters) == 3

        # Check first parameter - all parameters are now optional with initial values
        param1 = parameters[0]
        assert param1.name == "customer_name"
        assert param1.type == "string"
        assert param1.description == "Customer's full name"
        assert param1.required is False  # All variables are optional now
        assert param1.default is None  # Empty string coerced to None

        # Check parameter with non-empty default value
        param3 = parameters[2]
        assert param3.name == "company"
        assert param3.required is False
        assert param3.default == "Default Corp"

    def test_extract_parameters_from_legacy_start_step(
        self, mcp_config, legacy_flow_config
    ):
        """Test parameter extraction from legacy START step for backward compatibility."""
        generator = ToolGenerator(mcp_config)

        parameters = generator.extract_parameters_from_variables_step(
            legacy_flow_config
        )

        assert len(parameters) == 1
        assert parameters[0].name == "customer_id"
        assert parameters[0].required is False

    def test_extract_parameters_no_start_step(self, mcp_config):
        """Test parameter extraction when no START step exists."""
        generator = ToolGenerator(mcp_config)

        flow_config = FlowConfig(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            name="Test Flow",
            description="Test",
            steps=[{"id": "step-1", "type": "api_call", "config": {}}],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            status="active",
            tags=[],
        )

        parameters = generator.extract_parameters_from_variables_step(flow_config)

        assert len(parameters) == 0

    def test_extract_parameters_unsupported_dict_format(self, mcp_config):
        """Test parameter extraction with unsupported dict format variables."""
        generator = ToolGenerator(mcp_config)

        flow_config = FlowConfig(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            name="Test Flow",
            description="Test",
            steps=[
                {
                    "id": "start-1",
                    "type": "start",
                    "config": {
                        "variables": {
                            "input_text": {
                                "type": "string",
                                "description": "Input text",
                                "required": True,
                            },
                            "simple_var": "default_value",
                        }
                    },
                }
            ],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            status="active",
            tags=[],
        )

        parameters = generator.extract_parameters_from_variables_step(flow_config)

        # Dict format is no longer supported, should return empty list
        assert len(parameters) == 0

    def test_map_variable_type(self, mcp_config):
        """Test variable type mapping."""
        generator = ToolGenerator(mcp_config)

        assert generator._map_variable_type("string") == "string"
        assert generator._map_variable_type("text") == "string"
        assert generator._map_variable_type("number") == "number"
        assert generator._map_variable_type("integer") == "integer"
        assert generator._map_variable_type("int") == "integer"
        assert generator._map_variable_type("boolean") == "boolean"
        assert generator._map_variable_type("bool") == "boolean"
        assert generator._map_variable_type("array") == "array"
        assert generator._map_variable_type("list") == "array"
        assert generator._map_variable_type("object") == "object"
        assert generator._map_variable_type("dict") == "object"
        assert generator._map_variable_type("unknown") == "string"  # Default

    def test_create_input_schema_empty(self, mcp_config):
        """Test creating input schema with no parameters."""
        generator = ToolGenerator(mcp_config)

        schema = generator.create_input_schema([])

        expected = {"type": "object", "properties": {}, "required": []}

        assert schema == expected

    def test_create_input_schema_with_parameters(self, mcp_config):
        """Test creating input schema with parameters."""
        generator = ToolGenerator(mcp_config)

        parameters = [
            ToolParameter(
                name="name", type="string", description="User name", required=True
            ),
            ToolParameter(
                name="age",
                type="integer",
                description="User age",
                required=False,
                default=0,
            ),
        ]

        schema = generator.create_input_schema(parameters)

        assert schema["type"] == "object"
        assert "name" in schema["properties"]
        assert "age" in schema["properties"]
        assert schema["required"] == ["name"]
        assert schema["properties"]["name"]["type"] == "string"
        assert schema["properties"]["age"]["default"] == 0

    def test_generate_tool_from_flow(self, mcp_config, sample_flow_config):
        """Test generating a complete tool from flow."""
        generator = ToolGenerator(mcp_config)

        tool = generator.generate_tool_from_flow(sample_flow_config)

        assert tool.name == "test_customer_onboarding_flow"
        assert tool.description == "Automated customer onboarding process"
        assert tool.flow_id == "550e8400-e29b-41d4-a716-446655440000"
        assert tool.flow_name == "Customer Onboarding Flow"
        assert len(tool.parameters) == 3

        # Check MCP tool
        assert isinstance(tool.mcp_tool, Tool)
        assert tool.mcp_tool.name == tool.name
        assert tool.mcp_tool.description == tool.description

    def test_validate_tool_parameters_valid(self, mcp_config):
        """Test validating valid tool parameters."""
        generator = ToolGenerator(mcp_config)

        params = {"name": "John", "age": 30, "active": True}

        result = generator.validate_tool_parameters("test_tool", params)

        assert result == params

    def test_validate_tool_parameters_with_none(self, mcp_config):
        """Test validating tool parameters with None values."""
        generator = ToolGenerator(mcp_config)

        params = {"name": "John", "age": None, "active": True}

        result = generator.validate_tool_parameters("test_tool", params)

        assert result == {"name": "John", "active": True}

    def test_validate_tool_parameters_invalid_type(self, mcp_config):
        """Test validating invalid tool parameters."""
        generator = ToolGenerator(mcp_config)

        with pytest.raises(ValueError, match="Parameters must be a dictionary"):
            generator.validate_tool_parameters("test_tool", "invalid")

    def test_clear_generated_names(self, mcp_config):
        """Test clearing generated names."""
        generator = ToolGenerator(mcp_config)

        # Generate a name
        generator.sanitize_tool_name("Test Flow", "flow-123")
        assert len(generator._generated_names) == 1

        # Clear names
        generator.clear_generated_names()
        assert len(generator._generated_names) == 0

    def test_get_generation_stats(self, mcp_config):
        """Test getting generation statistics."""
        generator = ToolGenerator(mcp_config)

        # Generate some names
        generator.sanitize_tool_name("Flow 1", "550e8400-e29b-41d4-a716-446655440000")
        generator.sanitize_tool_name("Flow 2", "flow-2")

        stats = generator.get_generation_stats()

        assert stats["generated_names_count"] == 2
        assert stats["tool_name_prefix"] == "test"
        assert stats["max_tool_name_length"] == 64

    def test_infer_array_item_type_string(self, mcp_config):
        """Test array item type inference for string arrays."""
        generator = ToolGenerator(mcp_config)

        # Test string array
        string_array = ["https://techcrunch.com", "https://www.reuters.com"]
        item_type = generator._infer_array_item_type(string_array)
        assert item_type == "string"

    def test_infer_array_item_type_number(self, mcp_config):
        """Test array item type inference for number arrays."""
        generator = ToolGenerator(mcp_config)

        # Test integer array
        int_array = [1, 2, 3]
        item_type = generator._infer_array_item_type(int_array)
        assert item_type == "integer"

        # Test float array
        float_array = [1.5, 2.7, 3.14]
        item_type = generator._infer_array_item_type(float_array)
        assert item_type == "number"

    def test_infer_array_item_type_boolean(self, mcp_config):
        """Test array item type inference for boolean arrays."""
        generator = ToolGenerator(mcp_config)

        bool_array = [True, False, True]
        item_type = generator._infer_array_item_type(bool_array)
        assert item_type == "boolean"

    def test_infer_array_item_type_empty(self, mcp_config):
        """Test array item type inference for empty arrays."""
        generator = ToolGenerator(mcp_config)

        empty_array = []
        item_type = generator._infer_array_item_type(empty_array)
        assert item_type == "string"  # Default fallback

    def test_create_input_schema_with_array_parameters(self, mcp_config):
        """Test creating input schema with array parameters."""
        generator = ToolGenerator(mcp_config)

        parameters = [
            ToolParameter(
                name="news_sources",
                type="array",
                description="List of news sources to scrape",
                required=False,
                default=["https://techcrunch.com", "https://www.reuters.com"],
            ),
            ToolParameter(
                name="scraped_articles",
                type="array",
                description="Array to store scraped article content",
                required=False,
                default=[],
            ),
            ToolParameter(
                name="retry_counts",
                type="array",
                description="Retry counts for each source",
                required=False,
                default=[1, 2, 3],
            ),
        ]

        schema = generator.create_input_schema(parameters)

        # Check news_sources (string array)
        news_sources_schema = schema["properties"]["news_sources"]
        assert news_sources_schema["type"] == "array"
        assert news_sources_schema["items"]["type"] == "string"
        assert news_sources_schema["default"] == [
            "https://techcrunch.com",
            "https://www.reuters.com",
        ]

        # Check scraped_articles (empty array defaults to string items)
        scraped_articles_schema = schema["properties"]["scraped_articles"]
        assert scraped_articles_schema["type"] == "array"
        assert scraped_articles_schema["items"]["type"] == "string"
        assert scraped_articles_schema["default"] == []

        # Check retry_counts (integer array)
        retry_counts_schema = schema["properties"]["retry_counts"]
        assert retry_counts_schema["type"] == "array"
        assert retry_counts_schema["items"]["type"] == "integer"
        assert retry_counts_schema["default"] == [1, 2, 3]

    def test_extract_parameters_with_real_flow_example(self, mcp_config):
        """Test parameter extraction with a real flow example from the user."""
        generator = ToolGenerator(mcp_config)

        # Create flow config based on the user's example
        flow_config = FlowConfig(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            name="Breaking News LinkedIn Post Generator",
            description="Generate LinkedIn posts from breaking news",
            steps=[
                {
                    "id": "start-1",
                    "type": "start",
                    "config": {
                        "variables": [
                            {
                                "name": "breaking_news_topic",
                                "type": "string",
                                "value": "AI development",
                                "description": "The breaking news topic/keywords to search for",
                            },
                            {
                                "name": "max_scrape_attempts",
                                "type": "number",
                                "value": 1,
                                "description": "Maximum number of scraping attempts per news source",
                            },
                            {
                                "name": "news_sources",
                                "type": "array",
                                "value": ["https://techcrunch.com"],
                                "description": "List of news sources to scrape",
                            },
                            {
                                "name": "scraped_articles",
                                "type": "array",
                                "value": [],
                                "description": "Array to store scraped article content",
                            },
                            {
                                "name": "notification_email",
                                "type": "string",
                                "value": "taicai@rtanalytics.vn",
                                "description": "Email address to send the generated LinkedIn post to",
                            },
                        ]
                    },
                }
            ],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            status="active",
            tags=["news", "linkedin"],
        )

        parameters = generator.extract_parameters_from_variables_step(flow_config)

        assert len(parameters) == 5

        # Check string parameter
        topic_param = next(p for p in parameters if p.name == "breaking_news_topic")
        assert topic_param.type == "string"
        assert topic_param.default == "AI development"
        assert topic_param.required is False

        # Check number parameter
        attempts_param = next(p for p in parameters if p.name == "max_scrape_attempts")
        assert attempts_param.type == "number"
        assert attempts_param.default == 1
        assert attempts_param.required is False

        # Check array parameters
        sources_param = next(p for p in parameters if p.name == "news_sources")
        assert sources_param.type == "array"
        assert sources_param.default == ["https://techcrunch.com"]
        assert sources_param.required is False

        articles_param = next(p for p in parameters if p.name == "scraped_articles")
        assert articles_param.type == "array"
        assert articles_param.default == []
        assert articles_param.required is False

        # Test the generated schema
        schema = generator.create_input_schema(parameters)

        # Verify array schemas have proper items
        news_sources_schema = schema["properties"]["news_sources"]
        assert news_sources_schema["type"] == "array"
        assert news_sources_schema["items"]["type"] == "string"
        assert news_sources_schema["default"] == ["https://techcrunch.com"]

        scraped_articles_schema = schema["properties"]["scraped_articles"]
        assert scraped_articles_schema["type"] == "array"
        assert (
            scraped_articles_schema["items"]["type"] == "string"
        )  # Empty array defaults to string
        assert scraped_articles_schema["default"] == []

    def test_extract_parameters_with_source_filtering(self, mcp_config):
        """Test parameter extraction with source field filtering."""
        generator = ToolGenerator(mcp_config)

        flow_config = FlowConfig(
            uuid="550e8400-e29b-41d4-a716-446655440000",
            name="Flow with Source Filtering",
            description="Test flow with source filtering",
            steps=[
                {
                    "id": "start-1",
                    "type": "start",
                    "config": {
                        "variables": [
                            {
                                "name": "user_query",
                                "type": "string",
                                "value": "",
                                "description": "User provided query",
                                "source": "user_input",  # Should be included
                            },
                            {
                                "name": "search_results",
                                "type": "array",
                                "value": [],
                                "description": "Search results from previous step",
                                "source": "node_output",  # Should be excluded
                            },
                            {
                                "name": "api_endpoint",
                                "type": "string",
                                "value": "https://api.example.com",
                                "description": "System API endpoint",
                                "source": "system",  # Should be excluded
                            },
                            {
                                "name": "max_results",
                                "type": "number",
                                "value": 10,
                                "description": "Maximum results to return",
                                # Missing source - should default to user_input and be included
                            },
                        ]
                    },
                }
            ],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            status="active",
            tags=["test"],
        )

        parameters = generator.extract_parameters_from_variables_step(flow_config)

        # Should only include variables with source="user_input" or missing source
        assert len(parameters) == 2

        param_names = [p.name for p in parameters]
        assert "user_query" in param_names  # source="user_input"
        assert "max_results" in param_names  # source missing (defaults to "user_input")
        assert "search_results" not in param_names  # source="node_output"
        assert "api_endpoint" not in param_names  # source="system"

        # Verify the included parameters
        user_query_param = next(p for p in parameters if p.name == "user_query")
        assert user_query_param.type == "string"
        assert user_query_param.description == "User provided query"

        max_results_param = next(p for p in parameters if p.name == "max_results")
        assert max_results_param.type == "number"
        assert max_results_param.default == 10
