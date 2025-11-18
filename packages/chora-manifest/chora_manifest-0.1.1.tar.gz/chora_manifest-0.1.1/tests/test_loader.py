"""Tests for chora-manifest YAML registry loader.

Following TDD: Write tests first, then implement.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from manifest.core.models import Capability, Category


def test_load_valid_registry():
    """Test loading a valid registry YAML file."""
    from manifest.core.loader import RegistryLoader

    # Create temporary registry file
    registry_data = {
        "version": "1.0.0",
        "updated": "2025-11-15T00:00:00Z",
        "servers": [
            {
                "server": {
                    "name": "github",
                    "description": "GitHub integration",
                    "version": "1.0.0",
                    "repository": "https://github.com/example/github-mcp",
                    "transport": "stdio",
                },
                "tools": [
                    {
                        "name": "create_file",
                        "description": "Create a file",
                        "input_schema": {"type": "object"},
                    }
                ],
                "metadata": {"tags": ["integration", "version-control"]},
            }
        ],
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)

    try:
        loader = RegistryLoader(temp_path)
        capabilities = loader.load()

        assert len(capabilities) == 1
        assert isinstance(capabilities[0], Capability)
        assert capabilities[0].id == "github"
        assert capabilities[0].name == "github"
        assert capabilities[0].description == "GitHub integration"
        assert len(capabilities[0].tools) == 1
        assert "integration" in capabilities[0].tags
    finally:
        temp_path.unlink()


def test_load_multiple_servers():
    """Test loading registry with multiple servers."""
    from manifest.core.loader import RegistryLoader

    registry_data = {
        "version": "1.0.0",
        "servers": [
            {
                "server": {"name": "github", "description": "Git", "version": "1.0.0"},
                "tools": [],
                "metadata": {"tags": ["integration"]},
            },
            {
                "server": {"name": "slack", "description": "Chat", "version": "1.0.0"},
                "tools": [],
                "metadata": {"tags": ["productivity"]},
            },
        ],
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)

    try:
        loader = RegistryLoader(temp_path)
        capabilities = loader.load()

        assert len(capabilities) == 2
        assert capabilities[0].id == "github"
        assert capabilities[1].id == "slack"
    finally:
        temp_path.unlink()


def test_load_file_not_found():
    """Test that loading non-existent file raises FileNotFoundError."""
    from manifest.core.loader import RegistryLoader

    loader = RegistryLoader(Path("/nonexistent/registry.yaml"))

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_load_invalid_yaml():
    """Test that invalid YAML raises appropriate error."""
    from manifest.core.loader import RegistryLoader

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        f.write("invalid: yaml: content: [unclosed")
        temp_path = Path(f.name)

    try:
        loader = RegistryLoader(temp_path)

        with pytest.raises(yaml.YAMLError):
            loader.load()
    finally:
        temp_path.unlink()


def test_category_detection_from_tags():
    """Test that category is inferred from tags."""
    from manifest.core.loader import RegistryLoader

    registry_data = {
        "version": "1.0.0",
        "servers": [
            {
                "server": {"name": "postgres", "description": "DB", "version": "1.0.0"},
                "tools": [],
                "metadata": {"tags": ["database", "sql"]},
            }
        ],
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)

    try:
        loader = RegistryLoader(temp_path)
        capabilities = loader.load()

        assert capabilities[0].category == Category.DATABASE
    finally:
        temp_path.unlink()


def test_docker_image_generation():
    """Test that docker_image is generated from name and version."""
    from manifest.core.loader import RegistryLoader

    registry_data = {
        "version": "1.0.0",
        "servers": [
            {
                "server": {"name": "test-server", "description": "Test", "version": "2.0.0"},
                "tools": [],
                "metadata": {"tags": []},
            }
        ],
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)

    try:
        loader = RegistryLoader(temp_path)
        capabilities = loader.load()

        # Docker image should be generated as name:version or similar
        assert capabilities[0].docker_image is not None
        assert "test-server" in capabilities[0].docker_image
    finally:
        temp_path.unlink()


def test_empty_registry():
    """Test loading registry with no servers."""
    from manifest.core.loader import RegistryLoader

    registry_data = {"version": "1.0.0", "servers": []}

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)

    try:
        loader = RegistryLoader(temp_path)
        capabilities = loader.load()

        assert capabilities == []
    finally:
        temp_path.unlink()


def test_repository_url_extracted():
    """Test that repository URL is extracted from server metadata."""
    from manifest.core.loader import RegistryLoader

    registry_data = {
        "version": "1.0.0",
        "servers": [
            {
                "server": {
                    "name": "github",
                    "description": "GitHub",
                    "version": "1.0.0",
                    "repository": "https://github.com/example/github-mcp",
                },
                "tools": [],
                "metadata": {"tags": []},
            }
        ],
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)

    try:
        loader = RegistryLoader(temp_path)
        capabilities = loader.load()

        assert capabilities[0].repository == "https://github.com/example/github-mcp"
    finally:
        temp_path.unlink()


def test_tools_extraction():
    """Test that tools are correctly extracted and formatted."""
    from manifest.core.loader import RegistryLoader

    registry_data = {
        "version": "1.0.0",
        "servers": [
            {
                "server": {"name": "test", "description": "Test", "version": "1.0.0"},
                "tools": [
                    {
                        "name": "tool1",
                        "description": "First tool",
                        "input_schema": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "tool2",
                        "description": "Second tool",
                        "input_schema": {"type": "string"},
                    },
                ],
                "metadata": {"tags": []},
            }
        ],
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)

    try:
        loader = RegistryLoader(temp_path)
        capabilities = loader.load()

        assert len(capabilities[0].tools) == 2
        assert capabilities[0].tools[0]["name"] == "tool1"
        assert capabilities[0].tools[1]["name"] == "tool2"
    finally:
        temp_path.unlink()


def test_default_category_if_no_tags():
    """Test that a default category is assigned if no recognizable tags."""
    from manifest.core.loader import RegistryLoader

    registry_data = {
        "version": "1.0.0",
        "servers": [
            {
                "server": {"name": "unknown", "description": "Unknown", "version": "1.0.0"},
                "tools": [],
                "metadata": {"tags": ["random", "tags"]},
            }
        ],
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)

    try:
        loader = RegistryLoader(temp_path)
        capabilities = loader.load()

        # Should have a category (even if default)
        assert capabilities[0].category in [
            Category.INTEGRATION,
            Category.DATABASE,
            Category.PRODUCTIVITY,
            Category.INFRASTRUCTURE,
        ]
    finally:
        temp_path.unlink()
