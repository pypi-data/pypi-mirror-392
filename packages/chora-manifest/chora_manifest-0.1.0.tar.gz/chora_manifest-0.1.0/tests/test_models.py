"""Tests for chora-manifest core models.

Following TDD approach: Write tests first, then implement.
"""

import pytest
from pydantic import ValidationError


def test_category_enum_values():
    """Test Category enum has expected values."""
    from manifest.core.models import Category

    assert Category.INTEGRATION == "integration"
    assert Category.DATABASE == "database"
    assert Category.PRODUCTIVITY == "productivity"
    assert Category.INFRASTRUCTURE == "infrastructure"

    # Test all values are strings
    for category in Category:
        assert isinstance(category.value, str)


def test_capability_minimal_creation():
    """Test creating Capability with minimal required fields."""
    from manifest.core.models import Capability, Category

    capability = Capability(
        id="test-server",
        name="Test Server",
        description="A test MCP server",
        version="1.0.0",
        docker_image="test/server:1.0.0",
        tools=[],
        category=Category.INTEGRATION,
    )

    assert capability.id == "test-server"
    assert capability.name == "Test Server"
    assert capability.description == "A test MCP server"
    assert capability.version == "1.0.0"
    assert capability.docker_image == "test/server:1.0.0"
    assert capability.tools == []
    assert capability.category == Category.INTEGRATION
    assert capability.tags == []  # Default empty list
    assert capability.repository is None  # Optional field


def test_capability_with_tools():
    """Test Capability with tool definitions."""
    from manifest.core.models import Capability, Category

    tools = [
        {
            "name": "create_file",
            "description": "Create a new file",
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
            },
        }
    ]

    capability = Capability(
        id="github",
        name="GitHub",
        description="GitHub integration",
        version="1.0.0",
        docker_image="github:1.0.0",
        tools=tools,
        category=Category.INTEGRATION,
    )

    assert len(capability.tools) == 1
    assert capability.tools[0]["name"] == "create_file"
    assert capability.tools[0]["description"] == "Create a new file"


def test_capability_with_optional_fields():
    """Test Capability with all optional fields populated."""
    from manifest.core.models import Capability, Category

    capability = Capability(
        id="postgres",
        name="PostgreSQL",
        description="Database server",
        version="2.0.0",
        docker_image="postgres:2.0.0",
        tools=[],
        category=Category.DATABASE,
        tags=["sql", "database", "relational"],
        repository="https://github.com/example/postgres-mcp",
    )

    assert capability.tags == ["sql", "database", "relational"]
    assert capability.repository == "https://github.com/example/postgres-mcp"


def test_capability_missing_required_field():
    """Test that creating Capability without required fields raises ValidationError."""
    from manifest.core.models import Capability

    with pytest.raises(ValidationError) as exc_info:
        Capability(
            id="incomplete",
            name="Incomplete Server",
            # Missing: description, version, docker_image, tools, category
        )

    # Check that validation error mentions missing fields
    error_dict = exc_info.value.errors()
    missing_fields = {err["loc"][0] for err in error_dict}
    assert "description" in missing_fields
    assert "version" in missing_fields
    assert "docker_image" in missing_fields
    assert "tools" in missing_fields
    assert "category" in missing_fields


def test_capability_invalid_category():
    """Test that invalid category string is rejected."""
    from manifest.core.models import Capability

    with pytest.raises(ValidationError) as exc_info:
        Capability(
            id="bad-category",
            name="Bad Category",
            description="Server with invalid category",
            version="1.0.0",
            docker_image="bad:1.0.0",
            tools=[],
            category="invalid_category",  # Not a valid Category enum value
        )

    # Check error relates to category field
    error_dict = exc_info.value.errors()
    assert any(err["loc"][0] == "category" for err in error_dict)


def test_capability_dict_export():
    """Test that Capability can be exported to dict."""
    from manifest.core.models import Capability, Category

    capability = Capability(
        id="slack",
        name="Slack",
        description="Slack integration",
        version="1.0.0",
        docker_image="slack:1.0.0",
        tools=[{"name": "send_message", "description": "Send message"}],
        category=Category.PRODUCTIVITY,
        tags=["messaging"],
    )

    data = capability.model_dump()

    assert data["id"] == "slack"
    assert data["name"] == "Slack"
    assert data["category"] == "productivity"  # Enum value as string
    assert data["tags"] == ["messaging"]
    assert data["repository"] is None


def test_capability_json_serialization():
    """Test that Capability can be serialized to JSON."""
    from manifest.core.models import Capability, Category

    capability = Capability(
        id="jira",
        name="Jira",
        description="Jira integration",
        version="1.0.0",
        docker_image="jira:1.0.0",
        tools=[],
        category=Category.PRODUCTIVITY,
    )

    json_str = capability.model_dump_json()

    assert '"id":"jira"' in json_str or '"id": "jira"' in json_str
    assert (
        '"category":"productivity"' in json_str
        or '"category": "productivity"' in json_str
    )


def test_multiple_capabilities_different_categories():
    """Test creating multiple capabilities with different categories."""
    from manifest.core.models import Capability, Category

    github = Capability(
        id="github",
        name="GitHub",
        description="Git",
        version="1.0.0",
        docker_image="github:1.0.0",
        tools=[],
        category=Category.INTEGRATION,
    )

    postgres = Capability(
        id="postgres",
        name="PostgreSQL",
        description="DB",
        version="1.0.0",
        docker_image="postgres:1.0.0",
        tools=[],
        category=Category.DATABASE,
    )

    slack = Capability(
        id="slack",
        name="Slack",
        description="Chat",
        version="1.0.0",
        docker_image="slack:1.0.0",
        tools=[],
        category=Category.PRODUCTIVITY,
    )

    docker = Capability(
        id="docker",
        name="Docker",
        description="Containers",
        version="1.0.0",
        docker_image="docker:1.0.0",
        tools=[],
        category=Category.INFRASTRUCTURE,
    )

    capabilities = [github, postgres, slack, docker]
    categories = [c.category for c in capabilities]

    assert Category.INTEGRATION in categories
    assert Category.DATABASE in categories
    assert Category.PRODUCTIVITY in categories
    assert Category.INFRASTRUCTURE in categories
