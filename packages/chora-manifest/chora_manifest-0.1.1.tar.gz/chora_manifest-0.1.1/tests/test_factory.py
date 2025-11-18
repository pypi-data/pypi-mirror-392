"""Tests for chora-manifest factory function.

Following TDD: Write tests first, then implement.
"""

import tempfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def sample_registry_file():
    """Create a simple registry file for testing."""
    registry_data = {
        "version": "1.0.0",
        "servers": [
            {
                "server": {
                    "name": "test-server",
                    "description": "Test server",
                    "version": "1.0.0",
                },
                "tools": [],
                "metadata": {"tags": ["integration"]},
            }
        ],
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as f:
        yaml.dump(registry_data, f)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink()


def test_factory_function_exists():
    """Test that create_manifest_service factory function exists."""
    from manifest.core import create_manifest_service

    assert callable(create_manifest_service)


def test_factory_creates_service_with_default_path():
    """Test factory creates ManifestService with default path."""
    from manifest.core import create_manifest_service
    from manifest.core.service import ManifestService

    service = create_manifest_service()

    assert isinstance(service, ManifestService)
    assert service.registry_path is not None


def test_factory_creates_service_with_custom_path(sample_registry_file):
    """Test factory creates ManifestService with custom path."""
    from manifest.core import create_manifest_service
    from manifest.core.service import ManifestService

    service = create_manifest_service(sample_registry_file)

    assert isinstance(service, ManifestService)
    assert service.registry_path == sample_registry_file


def test_factory_returns_uninitialized_service():
    """Test factory returns service that needs initialization."""
    from manifest.core import create_manifest_service

    service = create_manifest_service()

    # Service should not be initialized yet
    assert not service._initialized


@pytest.mark.asyncio
async def test_factory_service_can_be_initialized(sample_registry_file):
    """Test that service from factory can be initialized and used."""
    from manifest.core import create_manifest_service

    # Create service using factory
    service = create_manifest_service(sample_registry_file)

    # Initialize it
    await service.initialize()

    # Should be able to use it
    capabilities = await service.list_capabilities()
    assert len(capabilities) == 1
    assert capabilities[0].id == "test-server"


@pytest.mark.asyncio
async def test_complete_workflow_with_factory(sample_registry_file):
    """Test complete workflow: factory → initialize → query."""
    from manifest.core import create_manifest_service

    # Step 1: Create service
    service = create_manifest_service(sample_registry_file)

    # Step 2: Initialize
    await service.initialize()

    # Step 3: Use service methods
    total = await service.count_total()
    assert total == 1

    capability = await service.get_capability("test-server")
    assert capability is not None
    assert capability.name == "test-server"


def test_factory_accepts_none_explicitly():
    """Test factory accepts None for registry_path parameter."""
    from manifest.core import create_manifest_service

    # Should work with explicit None
    service = create_manifest_service(registry_path=None)

    assert service is not None
    assert service.registry_path is not None  # Should have default


def test_factory_accepts_path_object(sample_registry_file):
    """Test factory accepts Path object."""
    from manifest.core import create_manifest_service

    service = create_manifest_service(sample_registry_file)

    assert service.registry_path == sample_registry_file


def test_factory_accepts_string_path(sample_registry_file):
    """Test factory accepts string path (converts to Path)."""
    from manifest.core import create_manifest_service

    # Pass as string
    service = create_manifest_service(str(sample_registry_file))

    # Should be converted to Path internally
    assert isinstance(service.registry_path, Path)
    assert service.registry_path == sample_registry_file


def test_public_api_exports():
    """Test that all expected symbols are exported from manifest.core."""
    import manifest.core

    # Check all required exports exist
    assert hasattr(manifest.core, "Capability")
    assert hasattr(manifest.core, "Category")
    assert hasattr(manifest.core, "ManifestService")
    assert hasattr(manifest.core, "RegistryLoader")
    assert hasattr(manifest.core, "create_manifest_service")

    # Check __all__ is defined
    assert hasattr(manifest.core, "__all__")
    assert "Capability" in manifest.core.__all__
    assert "Category" in manifest.core.__all__
    assert "ManifestService" in manifest.core.__all__
    assert "RegistryLoader" in manifest.core.__all__
    assert "create_manifest_service" in manifest.core.__all__


def test_top_level_package_exports():
    """Test that core symbols are available from top-level package."""
    import manifest

    # Should be able to import from top level
    assert hasattr(manifest, "Capability")
    assert hasattr(manifest, "Category")
    assert hasattr(manifest, "ManifestService")
    assert hasattr(manifest, "create_manifest_service")
