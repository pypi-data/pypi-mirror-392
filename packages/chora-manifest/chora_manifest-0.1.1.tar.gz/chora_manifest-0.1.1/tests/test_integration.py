"""
Integration tests for Feature 4: Ecosystem Discovery & Growth.

Tests the complete end-to-end workflow:
GitHub search → metadata extraction → YAML generation → aggregation
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
import yaml

from chora_manifest.core.aggregator import RegistryAggregator
from chora_manifest.core.bulk_importer import BulkImporter
from chora_manifest.core.models import GitHubQuery, RepositoryInfo


# ===================================================================
# Mock GitHub Response Data
# ===================================================================


def create_mock_nodejs_repo(name: str, stars: int = 10) -> RepositoryInfo:
    """Create mock Node.js MCP server repository."""
    return RepositoryInfo(
        name=name,
        full_name=f"testowner/{name}",
        url=f"https://github.com/testowner/{name}",
        description=f"{name} - MCP server for testing",
        stars=stars,
        language="TypeScript",
        topics=["mcp-server", "automation"],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2025, 11, 7),
        default_branch="main",
    )


def create_mock_python_repo(name: str, stars: int = 5) -> RepositoryInfo:
    """Create mock Python MCP server repository."""
    return RepositoryInfo(
        name=name,
        full_name=f"testowner/{name}",
        url=f"https://github.com/testowner/{name}",
        description=f"{name} - Python MCP server",
        stars=stars,
        language="Python",
        topics=["mcp-server", "python"],
        created_at=datetime(2024, 6, 1),
        updated_at=datetime(2025, 11, 7),
        default_branch="main",
    )


def mock_package_json(server_name: str):
    """Mock package.json for Node.js MCP server."""
    return {
        "name": server_name,
        "version": "1.0.0",
        "description": f"{server_name} - MCP server for testing",
        "main": "dist/index.js",
        "dependencies": {
            "@modelcontextprotocol/sdk": "^0.5.0",
        },
        "license": "MIT",
        "mcp": {
            "tools": [
                {
                    "name": "execute",
                    "description": "Execute a command",
                },
            ]
        },
    }


def mock_pyproject_toml(server_name: str):
    """Mock pyproject.toml for Python MCP server."""
    return f"""
[tool.poetry]
name = "{server_name}"
version = "0.1.0"
description = "{server_name} - Python MCP server"
authors = ["Test Author <test@example.com>"]
license = "MIT"

[tool.poetry.dependencies]
python = "^3.9"
mcp = "^0.1.0"

[tool.mcp]
transport = "stdio"

[[tool.mcp.tools]]
name = "process"
description = "Process data"
"""


# ===================================================================
# End-to-End Workflow Tests
# ===================================================================


@pytest.mark.asyncio
async def test_e2e_complete_discovery_workflow(tmp_path):
    """
    Test complete end-to-end workflow:
    GitHub search → metadata extraction → YAML generation → aggregation
    """
    # Step 1: Setup mock GitHub repositories
    mock_repos = [
        create_mock_nodejs_repo("mcp-server-typescript", stars=20),
        create_mock_nodejs_repo("mcp-server-automation", stars=15),
        create_mock_python_repo("mcp-server-python", stars=10),
    ]

    # Step 2: Import servers using BulkImporter
    output_dir = tmp_path / "server-entries"
    importer = BulkImporter(output_dir=output_dir)

    with patch.object(
        importer.github_client, "search_repositories", new_callable=AsyncMock
    ) as mock_search:
        with patch.object(
            importer.metadata_extractor, "_fetch_file", new_callable=AsyncMock
        ) as mock_fetch:
            mock_search.return_value = mock_repos

            # Mock file fetches for each repository
            def fetch_side_effect(repo, filename):
                if filename == "package.json":
                    if "python" not in repo.name:
                        return mock_package_json(repo.name)
                    return None
                elif filename == "pyproject.toml":
                    if "python" in repo.name:
                        return mock_pyproject_toml(repo.name)
                    return None
                return None

            mock_fetch.side_effect = fetch_side_effect

            # Execute import
            query = GitHubQuery(topics=["mcp-server"], min_stars=5)
            result = await importer.import_from_query(query)

    # Step 3: Verify import results
    assert result.total_attempted == 3
    assert result.successful == 3
    assert result.failed == 0
    assert len(result.servers_added) == 3

    # Step 4: Verify YAML files were created
    yaml_files = list(output_dir.glob("*.yaml"))
    assert len(yaml_files) == 3

    # Step 5: Aggregate server entries into registry
    registry_path = tmp_path / "registry.yaml"
    aggregator = RegistryAggregator()
    agg_result = aggregator.aggregate_to_yaml(output_dir, registry_path)

    # Step 6: Verify aggregation results
    assert agg_result.server_count == 3
    assert len(agg_result.errors) == 0
    assert registry_path.exists()

    # Step 7: Verify registry content
    with open(registry_path) as f:
        registry_data = yaml.safe_load(f)

    assert "servers" in registry_data
    assert len(registry_data["servers"]) == 3

    # Verify server names are sorted alphabetically
    server_names = [s["server"]["name"] for s in registry_data["servers"]]
    assert server_names == sorted(server_names)


@pytest.mark.asyncio
async def test_e2e_mixed_valid_invalid_servers(tmp_path):
    """
    Test workflow with mix of valid and invalid servers.
    Ensures invalid servers are filtered out during import.
    """
    # Create mix of valid and invalid repositories
    mock_repos = [
        create_mock_nodejs_repo("valid-mcp-server", stars=20),
        create_mock_nodejs_repo("invalid-no-sdk", stars=10),  # No MCP SDK
        create_mock_python_repo("valid-python-server", stars=15),
    ]

    output_dir = tmp_path / "server-entries"
    importer = BulkImporter(output_dir=output_dir)

    with patch.object(
        importer.github_client, "search_repositories", new_callable=AsyncMock
    ) as mock_search:
        with patch.object(
            importer.metadata_extractor, "_fetch_file", new_callable=AsyncMock
        ) as mock_fetch:
            mock_search.return_value = mock_repos

            def fetch_side_effect(repo, filename):
                if filename == "package.json":
                    if "invalid" in repo.name:
                        # Return package.json without MCP SDK
                        return {"name": repo.name, "version": "1.0.0"}
                    elif "python" not in repo.name:
                        return mock_package_json(repo.name)
                    return None
                elif filename == "pyproject.toml":
                    if "python" in repo.name:
                        return mock_pyproject_toml(repo.name)
                    return None
                return None

            mock_fetch.side_effect = fetch_side_effect

            query = GitHubQuery(topics=["mcp-server"])
            result = await importer.import_from_query(query)

    # Verify only valid servers were imported
    assert result.total_attempted == 3
    assert result.successful == 2
    assert result.failed == 1
    assert "invalid-no-sdk" not in result.servers_added

    # Verify only 2 YAML files created (valid servers only)
    yaml_files = list(output_dir.glob("*.yaml"))
    assert len(yaml_files) == 2


@pytest.mark.asyncio
async def test_e2e_overwrite_existing_entries(tmp_path):
    """
    Test importing servers twice with overwrite flag.
    """
    mock_repos = [create_mock_nodejs_repo("mcp-server-test", stars=10)]

    output_dir = tmp_path / "server-entries"
    importer = BulkImporter(output_dir=output_dir)

    with patch.object(
        importer.github_client, "search_repositories", new_callable=AsyncMock
    ) as mock_search:
        with patch.object(
            importer.metadata_extractor, "_fetch_file", new_callable=AsyncMock
        ) as mock_fetch:
            mock_search.return_value = mock_repos
            mock_fetch.side_effect = lambda repo, filename: (
                mock_package_json(repo.name) if filename == "package.json" else None
            )

            query = GitHubQuery(topics=["mcp-server"])

            # First import
            result1 = await importer.import_from_query(query, overwrite=False)
            assert result1.successful == 1

            # Second import without overwrite should fail
            result2 = await importer.import_from_query(query, overwrite=False)
            assert result2.successful == 0
            assert result2.failed == 1
            assert "already exists" in result2.errors.get(
                "testowner/mcp-server-test", ""
            )

            # Third import with overwrite should succeed
            result3 = await importer.import_from_query(query, overwrite=True)
            assert result3.successful == 1
            assert result3.failed == 0


@pytest.mark.asyncio
async def test_e2e_language_filtering(tmp_path):
    """
    Test filtering repositories by programming language.
    """
    mock_repos = [
        create_mock_nodejs_repo("typescript-server", stars=20),
        create_mock_python_repo("python-server", stars=15),
    ]

    output_dir = tmp_path / "server-entries"
    importer = BulkImporter(output_dir=output_dir)

    with patch.object(
        importer.github_client, "search_repositories", new_callable=AsyncMock
    ) as mock_search:
        with patch.object(
            importer.metadata_extractor, "_fetch_file", new_callable=AsyncMock
        ) as mock_fetch:
            # Only return TypeScript repos when language filter is set
            mock_search.return_value = [mock_repos[0]]  # Only TypeScript

            def fetch_side_effect(repo, filename):
                if filename == "package.json" and "typescript" in repo.name:
                    return mock_package_json(repo.name)
                return None

            mock_fetch.side_effect = fetch_side_effect

            query = GitHubQuery(topics=["mcp-server"], language="TypeScript")
            result = await importer.import_from_query(query)

    # Verify only TypeScript server imported
    assert result.successful == 1
    assert "typescript-server" in result.servers_added
    assert "python-server" not in result.servers_added


@pytest.mark.asyncio
async def test_e2e_min_stars_filtering(tmp_path):
    """
    Test filtering repositories by minimum stars.
    """
    mock_repos = [
        create_mock_nodejs_repo("popular-server", stars=50),
        create_mock_nodejs_repo("unpopular-server", stars=5),
    ]

    output_dir = tmp_path / "server-entries"
    importer = BulkImporter(output_dir=output_dir)

    with patch.object(
        importer.github_client, "search_repositories", new_callable=AsyncMock
    ) as mock_search:
        with patch.object(
            importer.metadata_extractor, "_fetch_file", new_callable=AsyncMock
        ) as mock_fetch:
            # Only return repos with >= 20 stars
            mock_search.return_value = [mock_repos[0]]  # Only popular server

            mock_fetch.side_effect = lambda repo, filename: (
                mock_package_json(repo.name) if filename == "package.json" else None
            )

            query = GitHubQuery(topics=["mcp-server"], min_stars=20)
            result = await importer.import_from_query(query)

    # Verify only popular server imported
    assert result.successful == 1
    assert "popular-server" in result.servers_added
    assert "unpopular-server" not in result.servers_added


# ===================================================================
# Aggregation Integration Tests
# ===================================================================


def test_e2e_aggregation_with_real_yaml_files(tmp_path):
    """
    Test aggregation with real YAML files created by ServerEntryGenerator.
    """
    # Create server-entries directory with manual YAML files
    entries_dir = tmp_path / "server-entries"
    entries_dir.mkdir()

    # Create sample server entries
    server1 = {
        "server": {
            "name": "alpha-server",
            "version": "1.0.0",
            "description": "Alpha MCP server",
            "repository": "https://github.com/testowner/alpha-server",
            "transport": "stdio",
        },
        "tools": [
            {
                "name": "execute",
                "description": "Execute command",
                "input_schema": {"type": "object", "properties": {}},
            }
        ],
        "metadata": {
            "maintainer": "testowner",
            "license": "MIT",
            "created": "2024-01-01T00:00:00Z",
            "updated": "2025-11-07T00:00:00Z",
        },
    }

    server2 = {
        "server": {
            "name": "zeta-server",
            "version": "2.0.0",
            "description": "Zeta MCP server",
            "repository": "https://github.com/testowner/zeta-server",
            "transport": "http",
        },
        "tools": [
            {
                "name": "process",
                "description": "Process data",
                "input_schema": {"type": "object", "properties": {}},
            }
        ],
        "metadata": {
            "maintainer": "testowner",
            "license": "BSD",
            "created": "2024-06-01T00:00:00Z",
            "updated": "2025-11-07T00:00:00Z",
        },
    }

    # Write YAML files
    with open(entries_dir / "alpha-server.yaml", "w") as f:
        yaml.dump(server1, f)

    with open(entries_dir / "zeta-server.yaml", "w") as f:
        yaml.dump(server2, f)

    # Aggregate entries
    registry_path = tmp_path / "registry.yaml"
    aggregator = RegistryAggregator()
    result = aggregator.aggregate_to_yaml(entries_dir, registry_path)

    # Verify aggregation
    assert result.server_count == 2
    assert len(result.errors) == 0

    # Load and verify registry
    with open(registry_path) as f:
        registry_data = yaml.safe_load(f)

    assert len(registry_data["servers"]) == 2

    # Verify alphabetical sorting (alpha before zeta)
    assert registry_data["servers"][0]["server"]["name"] == "alpha-server"
    assert registry_data["servers"][1]["server"]["name"] == "zeta-server"


# ===================================================================
# Error Handling Integration Tests
# ===================================================================


@pytest.mark.asyncio
async def test_e2e_github_api_timeout(tmp_path):
    """
    Test handling of GitHub API timeout during discovery.
    """
    output_dir = tmp_path / "server-entries"
    importer = BulkImporter(output_dir=output_dir)

    with patch.object(
        importer.github_client, "search_repositories", new_callable=AsyncMock
    ) as mock_search:
        mock_search.side_effect = TimeoutError("GitHub API timeout")

        query = GitHubQuery(topics=["mcp-server"])
        result = await importer.import_from_query(query)

    # Verify error handling
    assert result.total_attempted == 0
    assert result.successful == 0
    assert "github_search" in result.errors
    assert "timeout" in result.errors["github_search"].lower()


@pytest.mark.asyncio
async def test_e2e_metadata_extraction_failure(tmp_path):
    """
    Test handling of metadata extraction failures.
    """
    mock_repos = [
        create_mock_nodejs_repo("working-server", stars=20),
        create_mock_nodejs_repo("broken-server", stars=15),
    ]

    output_dir = tmp_path / "server-entries"
    importer = BulkImporter(output_dir=output_dir)

    with patch.object(
        importer.github_client, "search_repositories", new_callable=AsyncMock
    ) as mock_search:
        with patch.object(
            importer.metadata_extractor, "_fetch_file", new_callable=AsyncMock
        ) as mock_fetch:
            mock_search.return_value = mock_repos

            def fetch_side_effect(repo, filename):
                if "broken" in repo.name and filename == "package.json":
                    raise Exception("Network error fetching package.json")
                if filename == "package.json":
                    return mock_package_json(repo.name)
                return None

            mock_fetch.side_effect = fetch_side_effect

            query = GitHubQuery(topics=["mcp-server"])
            result = await importer.import_from_query(query)

    # Verify partial success
    assert result.total_attempted == 2
    assert result.successful == 1
    assert result.failed == 1
    assert "working-server" in result.servers_added
    assert "testowner/broken-server" in result.errors


def test_e2e_aggregation_duplicate_server_names(tmp_path):
    """
    Test aggregation fails when duplicate server names are found.
    """
    entries_dir = tmp_path / "server-entries"
    entries_dir.mkdir()

    # Create two servers with same name
    server = {
        "server": {
            "name": "duplicate-server",
            "version": "1.0.0",
            "description": "Duplicate server",
            "repository": "https://github.com/testowner/duplicate-server",
            "transport": "stdio",
        },
        "tools": [{"name": "execute", "description": "Execute", "input_schema": {}}],
        "metadata": {
            "maintainer": "testowner",
            "license": "MIT",
            "created": "2024-01-01T00:00:00Z",
            "updated": "2025-11-07T00:00:00Z",
        },
    }

    # Write same server to two different files
    with open(entries_dir / "duplicate-1.yaml", "w") as f:
        yaml.dump(server, f)

    with open(entries_dir / "duplicate-2.yaml", "w") as f:
        yaml.dump(server, f)

    # Try to aggregate
    registry_path = tmp_path / "registry.yaml"
    aggregator = RegistryAggregator()
    result = aggregator.aggregate_to_yaml(entries_dir, registry_path)

    # Verify duplicate error
    assert result.server_count == 0
    assert len(result.errors) > 0
    assert "duplicate" in result.errors[0].lower()


# ===================================================================
# Performance and Scale Tests
# ===================================================================


@pytest.mark.asyncio
async def test_e2e_large_batch_import(tmp_path):
    """
    Test importing a large batch of servers (10 servers).
    """
    # Create 10 mock repositories
    mock_repos = [
        create_mock_nodejs_repo(f"mcp-server-{i}", stars=10 + i) for i in range(10)
    ]

    output_dir = tmp_path / "server-entries"
    importer = BulkImporter(output_dir=output_dir)

    with patch.object(
        importer.github_client, "search_repositories", new_callable=AsyncMock
    ) as mock_search:
        with patch.object(
            importer.metadata_extractor, "_fetch_file", new_callable=AsyncMock
        ) as mock_fetch:
            mock_search.return_value = mock_repos
            mock_fetch.side_effect = lambda repo, filename: (
                mock_package_json(repo.name) if filename == "package.json" else None
            )

            query = GitHubQuery(topics=["mcp-server"], limit=10)
            result = await importer.import_from_query(query)

    # Verify all 10 servers imported
    assert result.total_attempted == 10
    assert result.successful == 10
    assert result.failed == 0
    assert len(result.servers_added) == 10

    # Verify all YAML files created
    yaml_files = list(output_dir.glob("*.yaml"))
    assert len(yaml_files) == 10

    # Aggregate all 10 servers
    registry_path = tmp_path / "registry.yaml"
    aggregator = RegistryAggregator()
    agg_result = aggregator.aggregate_to_yaml(output_dir, registry_path)

    assert agg_result.server_count == 10
    assert len(agg_result.errors) == 0


# ===================================================================
# Real-World Scenario Tests
# ===================================================================


@pytest.mark.asyncio
async def test_e2e_realistic_ecosystem_discovery(tmp_path):
    """
    Test realistic scenario: discover MCP servers from ecosystem.

    Simulates discovering servers with different:
    - Languages (TypeScript, Python)
    - Popularity (varying stars)
    - Completeness (some with tools, some without)
    """
    mock_repos = [
        # Popular TypeScript server with complete metadata
        RepositoryInfo(
            name="mcp-server-filesystem",
            full_name="anthropics/mcp-server-filesystem",
            url="https://github.com/anthropics/mcp-server-filesystem",
            description="MCP server for filesystem operations",
            stars=150,
            language="TypeScript",
            topics=["mcp-server", "filesystem", "tools"],
            created_at=datetime(2024, 1, 15),
            updated_at=datetime(2025, 11, 7),
            default_branch="main",
        ),
        # Python server with medium popularity
        RepositoryInfo(
            name="mcp-server-brave-search",
            full_name="liminalcommons/mcp-server-brave-search",
            url="https://github.com/liminalcommons/mcp-server-brave-search",
            description="MCP server for Brave Search API",
            stars=50,
            language="Python",
            topics=["mcp-server", "search", "brave"],
            created_at=datetime(2024, 6, 1),
            updated_at=datetime(2025, 11, 5),
            default_branch="main",
        ),
        # New TypeScript server with minimal metadata
        RepositoryInfo(
            name="mcp-server-minimal",
            full_name="developer/mcp-server-minimal",
            url="https://github.com/developer/mcp-server-minimal",
            description="Minimal MCP server example",
            stars=5,
            language="TypeScript",
            topics=["mcp-server"],
            created_at=datetime(2025, 10, 1),
            updated_at=datetime(2025, 11, 1),
            default_branch="main",
        ),
    ]

    output_dir = tmp_path / "server-entries"
    importer = BulkImporter(output_dir=output_dir)

    with patch.object(
        importer.github_client, "search_repositories", new_callable=AsyncMock
    ) as mock_search:
        with patch.object(
            importer.metadata_extractor, "_fetch_file", new_callable=AsyncMock
        ) as mock_fetch:
            mock_search.return_value = mock_repos

            def fetch_side_effect(repo, filename):
                if filename == "package.json" and repo.language == "TypeScript":
                    return mock_package_json(repo.name)
                elif filename == "pyproject.toml" and repo.language == "Python":
                    return mock_pyproject_toml(repo.name)
                return None

            mock_fetch.side_effect = fetch_side_effect

            query = GitHubQuery(topics=["mcp-server"], limit=50)
            result = await importer.import_from_query(query)

    # Verify all servers imported successfully
    assert result.successful == 3
    assert result.failed == 0

    # Aggregate into registry
    registry_path = tmp_path / "registry.yaml"
    aggregator = RegistryAggregator()
    agg_result = aggregator.aggregate_to_yaml(output_dir, registry_path)

    assert agg_result.server_count == 3

    # Verify registry structure
    with open(registry_path) as f:
        registry_data = yaml.safe_load(f)

    # Check servers are sorted alphabetically
    server_names = [s["server"]["name"] for s in registry_data["servers"]]
    assert server_names == sorted(server_names)

    # Verify different maintainers are preserved
    maintainers = {s["metadata"]["maintainer"] for s in registry_data["servers"]}
    assert len(maintainers) > 1  # Should have different owners
