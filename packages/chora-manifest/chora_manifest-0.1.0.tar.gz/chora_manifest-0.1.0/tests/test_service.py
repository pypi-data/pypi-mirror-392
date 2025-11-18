"""Tests for chora-manifest ManifestService.

Following TDD: Write tests first, then implement.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from manifest.core.models import Category


@pytest.fixture
def sample_registry_data():
    """Sample registry data for testing."""
    return {
        "version": "1.0.0",
        "updated": "2025-11-15T00:00:00Z",
        "servers": [
            {
                "server": {
                    "name": "github",
                    "description": "GitHub integration server",
                    "version": "1.0.0",
                    "repository": "https://github.com/example/github-mcp",
                },
                "tools": [
                    {"name": "create_file", "description": "Create a file"}
                ],
                "metadata": {"tags": ["integration", "version-control"]},
            },
            {
                "server": {
                    "name": "postgres",
                    "description": "PostgreSQL database server",
                    "version": "2.0.0",
                },
                "tools": [{"name": "query", "description": "Run SQL query"}],
                "metadata": {"tags": ["database", "sql"]},
            },
            {
                "server": {
                    "name": "slack",
                    "description": "Slack messaging integration",
                    "version": "1.5.0",
                },
                "tools": [
                    {"name": "send_message", "description": "Send a message"}
                ],
                "metadata": {"tags": ["productivity", "communication"]},
            },
            {
                "server": {
                    "name": "docker",
                    "description": "Docker container management",
                    "version": "3.0.0",
                },
                "tools": [{"name": "run", "description": "Run container"}],
                "metadata": {"tags": ["infrastructure", "containers"]},
            },
        ],
    }


@pytest.fixture
def registry_file(sample_registry_data):
    """Create temporary registry file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(sample_registry_data, f)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink()


@pytest.mark.asyncio
async def test_initialize_loads_registry(registry_file):
    """Test that initialize loads capabilities from registry."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    # Should have loaded 4 capabilities
    capabilities = await service.list_capabilities()
    assert len(capabilities) == 4


@pytest.mark.asyncio
async def test_initialize_with_default_path():
    """Test initialize with default registry path."""
    from manifest.core.service import ManifestService

    # Should accept None and use default path
    service = ManifestService(registry_path=None)

    # Initialize should work (may fail if default doesn't exist, which is fine)
    # This test just verifies the interface accepts None
    assert service.registry_path is not None


@pytest.mark.asyncio
async def test_list_capabilities_returns_all(registry_file):
    """Test list_capabilities returns all capabilities."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    capabilities = await service.list_capabilities()

    assert len(capabilities) == 4
    names = [c.name for c in capabilities]
    assert "github" in names
    assert "postgres" in names
    assert "slack" in names
    assert "docker" in names


@pytest.mark.asyncio
async def test_get_capability_by_id_found(registry_file):
    """Test get_capability returns capability when found."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    capability = await service.get_capability("github")

    assert capability is not None
    assert capability.id == "github"
    assert capability.name == "github"
    assert "GitHub" in capability.description


@pytest.mark.asyncio
async def test_get_capability_by_id_not_found(registry_file):
    """Test get_capability returns None when not found."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    capability = await service.get_capability("nonexistent")

    assert capability is None


@pytest.mark.asyncio
async def test_filter_by_category_integration(registry_file):
    """Test filter_by_category returns integration capabilities."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    capabilities = await service.filter_by_category(Category.INTEGRATION)

    assert len(capabilities) == 1
    assert capabilities[0].id == "github"
    assert capabilities[0].category == Category.INTEGRATION


@pytest.mark.asyncio
async def test_filter_by_category_database(registry_file):
    """Test filter_by_category returns database capabilities."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    capabilities = await service.filter_by_category(Category.DATABASE)

    assert len(capabilities) == 1
    assert capabilities[0].id == "postgres"
    assert capabilities[0].category == Category.DATABASE


@pytest.mark.asyncio
async def test_filter_by_category_productivity(registry_file):
    """Test filter_by_category returns productivity capabilities."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    capabilities = await service.filter_by_category(Category.PRODUCTIVITY)

    assert len(capabilities) == 1
    assert capabilities[0].id == "slack"
    assert capabilities[0].category == Category.PRODUCTIVITY


@pytest.mark.asyncio
async def test_filter_by_category_infrastructure(registry_file):
    """Test filter_by_category returns infrastructure capabilities."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    capabilities = await service.filter_by_category(Category.INFRASTRUCTURE)

    assert len(capabilities) == 1
    assert capabilities[0].id == "docker"
    assert capabilities[0].category == Category.INFRASTRUCTURE


@pytest.mark.asyncio
async def test_search_by_name(registry_file):
    """Test search finds capabilities by name."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    # Search for "slack"
    capabilities = await service.search("slack")

    assert len(capabilities) == 1
    assert capabilities[0].id == "slack"


@pytest.mark.asyncio
async def test_search_by_description(registry_file):
    """Test search finds capabilities by description."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    # Search for "database" (in postgres description)
    capabilities = await service.search("database")

    assert len(capabilities) >= 1
    assert any(c.id == "postgres" for c in capabilities)


@pytest.mark.asyncio
async def test_search_case_insensitive(registry_file):
    """Test search is case-insensitive."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    # Search with different cases
    lower = await service.search("github")
    upper = await service.search("GITHUB")
    mixed = await service.search("GitHub")

    assert len(lower) == len(upper) == len(mixed)
    assert lower[0].id == upper[0].id == mixed[0].id


@pytest.mark.asyncio
async def test_search_no_results(registry_file):
    """Test search returns empty list when no matches."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    capabilities = await service.search("nonexistent-query-xyz")

    assert capabilities == []


@pytest.mark.asyncio
async def test_count_total(registry_file):
    """Test count_total returns total number of capabilities."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    count = await service.count_total()

    assert count == 4


@pytest.mark.asyncio
async def test_count_by_category_integration(registry_file):
    """Test count_by_category for integration."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    count = await service.count_by_category(Category.INTEGRATION)

    assert count == 1


@pytest.mark.asyncio
async def test_count_by_category_database(registry_file):
    """Test count_by_category for database."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    count = await service.count_by_category(Category.DATABASE)

    assert count == 1


@pytest.mark.asyncio
async def test_count_by_category_productivity(registry_file):
    """Test count_by_category for productivity."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    count = await service.count_by_category(Category.PRODUCTIVITY)

    assert count == 1


@pytest.mark.asyncio
async def test_count_by_category_infrastructure(registry_file):
    """Test count_by_category for infrastructure."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    count = await service.count_by_category(Category.INFRASTRUCTURE)

    assert count == 1


@pytest.mark.asyncio
async def test_multiple_searches(registry_file):
    """Test multiple search queries work correctly."""
    from manifest.core.service import ManifestService

    service = ManifestService(registry_file)
    await service.initialize()

    # Search for "integration"
    integration_results = await service.search("integration")

    # Search for "container"
    container_results = await service.search("container")

    assert len(integration_results) >= 1
    assert len(container_results) >= 1
    assert integration_results[0].id != container_results[0].id


@pytest.mark.asyncio
async def test_empty_registry():
    """Test service with empty registry."""
    from manifest.core.service import ManifestService

    registry_data = {"version": "1.0.0", "servers": []}

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)

    try:
        service = ManifestService(temp_path)
        await service.initialize()

        capabilities = await service.list_capabilities()
        count = await service.count_total()

        assert capabilities == []
        assert count == 0
    finally:
        temp_path.unlink()


@pytest.mark.asyncio
async def test_service_methods_before_initialize():
    """Test that methods work before initialize (should handle gracefully)."""
    from manifest.core.service import ManifestService

    # Create temporary registry
    registry_data = {"version": "1.0.0", "servers": []}

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)

    try:
        service = ManifestService(temp_path)

        # Don't call initialize, try to use methods
        # Should either return empty results or raise helpful error
        # For now, let's expect it to initialize on first use (lazy loading)
        # or require explicit initialize

        # This test documents the expected behavior
        # Implementation should handle this gracefully
        capabilities = await service.list_capabilities()
        assert isinstance(capabilities, list)
    finally:
        temp_path.unlink()
