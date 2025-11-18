"""Core data models for chora-manifest.

Simplified models for v0.1.0: read-only service discovery.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Category(str, Enum):
    """MCP server capability categories."""

    INTEGRATION = "integration"
    DATABASE = "database"
    PRODUCTIVITY = "productivity"
    INFRASTRUCTURE = "infrastructure"


class Capability(BaseModel):
    """MCP server capability definition.

    Represents a registered MCP server with its metadata and tools.
    """

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(..., description="Unique identifier for the capability")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Brief description of the capability")
    version: str = Field(..., description="Semantic version (e.g., '1.0.0')")
    docker_image: str = Field(..., description="Docker image reference")
    tools: list[dict[str, Any]] = Field(
        ...,
        description="List of tool definitions (dicts with name, description, input_schema)",
    )
    category: Category = Field(..., description="Capability category")
    tags: list[str] = Field(default_factory=list, description="Searchable tags")
    repository: str | None = Field(
        default=None, description="Source repository URL (optional)"
    )
