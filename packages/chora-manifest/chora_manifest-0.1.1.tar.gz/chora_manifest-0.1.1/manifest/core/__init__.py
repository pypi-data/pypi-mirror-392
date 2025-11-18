"""Core package for chora-manifest.

Public API exports for models, loader, service, and factory.
"""

from pathlib import Path
from typing import Optional

from .loader import RegistryLoader
from .models import Capability, Category
from .service import ManifestService


def create_manifest_service(
    registry_path: Optional[Path | str] = None,
) -> ManifestService:
    """Create a ManifestService instance.

    Factory function for creating ManifestService with optional
    registry path. The service is created but not initialized -
    call await service.initialize() before using query methods.

    Args:
        registry_path: Path to registry YAML file. Can be Path object
                      or string. Defaults to ecosystem-manifest/registry.yaml
                      relative to current working directory.

    Returns:
        ManifestService instance (not yet initialized)

    Example:
        >>> service = create_manifest_service()
        >>> await service.initialize()
        >>> capabilities = await service.list_capabilities()
    """
    # Convert string to Path if needed
    if isinstance(registry_path, str):
        registry_path = Path(registry_path)

    return ManifestService(registry_path)


__all__ = [
    "Capability",
    "Category",
    "ManifestService",
    "RegistryLoader",
    "create_manifest_service",
]
