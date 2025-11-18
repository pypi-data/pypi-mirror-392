"""ManifestService for querying MCP server capabilities.

Provides async API for service discovery from registry.
"""

from pathlib import Path
from typing import Optional

from .loader import RegistryLoader
from .models import Capability, Category


class ManifestService:
    """Service for querying MCP server capabilities from registry.

    Provides async methods for listing, filtering, and searching
    registered MCP server capabilities.
    """

    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize service with registry file.

        Args:
            registry_path: Path to registry YAML. Defaults to
                          ecosystem-manifest/registry.yaml relative to cwd.
        """
        if registry_path is None:
            # Default path relative to current working directory
            self.registry_path = Path.cwd() / "ecosystem-manifest" / "registry.yaml"
        else:
            self.registry_path = registry_path

        self._capabilities: list[Capability] = []
        self._initialized = False

    async def initialize(self) -> None:
        """Load registry from file.

        Must be called before query methods. Loads capabilities into memory
        for fast querying.

        Raises:
            FileNotFoundError: If registry file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        loader = RegistryLoader(self.registry_path)
        self._capabilities = loader.load()
        self._initialized = True

    async def list_capabilities(self) -> list[Capability]:
        """List all registered capabilities.

        Returns:
            List of all Capability objects
        """
        if not self._initialized:
            await self.initialize()
        return self._capabilities.copy()

    async def get_capability(self, id: str) -> Optional[Capability]:
        """Get capability by ID.

        Args:
            id: Capability identifier (e.g., "github", "slack")

        Returns:
            Capability if found, None otherwise
        """
        if not self._initialized:
            await self.initialize()

        for capability in self._capabilities:
            if capability.id == id:
                return capability
        return None

    async def filter_by_category(self, category: Category) -> list[Capability]:
        """Filter capabilities by category.

        Args:
            category: Category enum value

        Returns:
            List of capabilities in the specified category
        """
        if not self._initialized:
            await self.initialize()

        return [c for c in self._capabilities if c.category == category]

    async def search(self, query: str) -> list[Capability]:
        """Search capabilities by name or description.

        Searches are case-insensitive and match against both name
        and description fields.

        Args:
            query: Search string

        Returns:
            List of capabilities matching the query
        """
        if not self._initialized:
            await self.initialize()

        query_lower = query.lower()
        results = []

        for capability in self._capabilities:
            # Search in name
            if query_lower in capability.name.lower():
                results.append(capability)
                continue

            # Search in description
            if query_lower in capability.description.lower():
                results.append(capability)
                continue

        return results

    async def count_total(self) -> int:
        """Count total capabilities.

        Returns:
            Total number of registered capabilities
        """
        if not self._initialized:
            await self.initialize()

        return len(self._capabilities)

    async def count_by_category(self, category: Category) -> int:
        """Count capabilities in a category.

        Args:
            category: Category enum value

        Returns:
            Number of capabilities in the category
        """
        if not self._initialized:
            await self.initialize()

        return sum(1 for c in self._capabilities if c.category == category)
