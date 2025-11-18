"""chora-manifest - MCP server service discovery and capability catalog.

v0.1.0: Read-only Python API for querying MCP server registry.
"""

from .core import (
    Capability,
    Category,
    ManifestService,
    RegistryLoader,
    create_manifest_service,
)

__version__ = "0.1.0"

__all__ = [
    "Capability",
    "Category",
    "ManifestService",
    "RegistryLoader",
    "create_manifest_service",
    "__version__",
]
