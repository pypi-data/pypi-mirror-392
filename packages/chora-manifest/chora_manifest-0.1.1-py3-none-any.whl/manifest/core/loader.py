"""YAML registry loader for chora-manifest.

Loads and parses MCP server registry from YAML format.
"""

from pathlib import Path
from typing import Any

import yaml

from .models import Capability, Category


class RegistryLoader:
    """Loads MCP server capabilities from YAML registry file.

    Converts the ecosystem-manifest "servers" format to Capability objects.
    """

    def __init__(self, registry_path: Path):
        """Initialize loader with registry file path.

        Args:
            registry_path: Path to registry YAML file
        """
        self.registry_path = registry_path

    def load(self) -> list[Capability]:
        """Load capabilities from registry file.

        Returns:
            List of Capability objects

        Raises:
            FileNotFoundError: If registry file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        if not self.registry_path.exists():
            raise FileNotFoundError(
                f"Registry file not found: {self.registry_path}"
            )

        with open(self.registry_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        servers = data.get("servers", [])
        return [self._parse_server_entry(server) for server in servers]

    def _parse_server_entry(self, entry: dict[str, Any]) -> Capability:
        """Parse a single server entry into a Capability.

        Args:
            entry: Server entry dict with 'server', 'tools', 'metadata' keys

        Returns:
            Capability object
        """
        server = entry.get("server", {})
        tools = entry.get("tools", [])
        metadata = entry.get("metadata", {})

        name = server.get("name", "")
        tags = metadata.get("tags", [])

        return Capability(
            id=name,  # Use server name as ID
            name=name,
            description=server.get("description", ""),
            version=server.get("version", "1.0.0"),
            docker_image=self._generate_docker_image(name, server.get("version", "1.0.0")),
            tools=tools,
            category=self._detect_category(tags),
            tags=tags,
            repository=server.get("repository"),
        )

    def _generate_docker_image(self, name: str, version: str) -> str:
        """Generate docker image reference from name and version.

        Args:
            name: Server name
            version: Server version

        Returns:
            Docker image reference (name:version)
        """
        return f"{name}:latest"

    def _detect_category(self, tags: list[str]) -> Category:
        """Detect category from tags.

        Args:
            tags: List of tag strings

        Returns:
            Category enum value
        """
        tags_lower = [tag.lower() for tag in tags]

        # Check for database indicators
        if any(tag in tags_lower for tag in ["database", "sql", "db", "postgres", "mysql"]):
            return Category.DATABASE

        # Check for productivity indicators
        if any(tag in tags_lower for tag in ["productivity", "slack", "jira", "communication"]):
            return Category.PRODUCTIVITY

        # Check for infrastructure indicators
        if any(tag in tags_lower for tag in ["infrastructure", "docker", "kubernetes", "deployment"]):
            return Category.INFRASTRUCTURE

        # Default to integration
        return Category.INTEGRATION
