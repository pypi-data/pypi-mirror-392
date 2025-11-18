"""
Test registry.yaml against registry.schema.json
"""

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import validate


# Paths
REPO_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = REPO_ROOT / "registry.yaml"
SCHEMA_PATH = REPO_ROOT / "chora_manifest" / "registry.schema.json"


@pytest.fixture
def registry():
    """Load registry.yaml"""
    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture
def schema():
    """Load registry.schema.json"""
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def test_registry_file_exists():
    """Verify registry.yaml exists"""
    assert REGISTRY_PATH.exists(), "registry.yaml not found"


def test_schema_file_exists():
    """Verify registry.schema.json exists"""
    assert SCHEMA_PATH.exists(), "registry.schema.json not found"


def test_registry_is_valid_yaml(registry):
    """Verify registry.yaml is valid YAML"""
    assert registry is not None
    assert isinstance(registry, dict)


def test_schema_is_valid_json(schema):
    """Verify registry.schema.json is valid JSON"""
    assert schema is not None
    assert isinstance(schema, dict)


def test_registry_validates_against_schema(registry, schema):
    """Verify registry.yaml validates against schema"""
    validate(instance=registry, schema=schema)


def test_registry_has_required_fields(registry):
    """Verify registry has required top-level fields"""
    assert "version" in registry
    assert "updated" in registry
    assert "servers" in registry


def test_registry_version_format(registry):
    """Verify registry version follows semver"""
    import re

    version = registry["version"]
    semver_pattern = r"^[0-9]+\.[0-9]+\.[0-9]+$"
    assert re.match(semver_pattern, version), f"Invalid version format: {version}"


def test_servers_is_list(registry):
    """Verify servers field is a list"""
    assert isinstance(registry["servers"], list)
    assert len(registry["servers"]) > 0, "No servers in registry"


def test_each_server_has_required_fields(registry):
    """Verify each server has required fields"""
    required_sections = ["server", "tools", "metadata"]

    for server in registry["servers"]:
        for section in required_sections:
            assert section in server, f"Missing {section} in server"


def test_server_names_unique(registry):
    """Verify server names are unique"""
    names = [s["server"]["name"] for s in registry["servers"]]
    assert len(names) == len(set(names)), "Duplicate server names found"


def test_server_info_fields(registry):
    """Verify server info has required fields"""
    required_fields = ["name", "description", "version", "repository", "transport"]

    for server in registry["servers"]:
        server_info = server["server"]
        for field in required_fields:
            assert (
                field in server_info
            ), f"Missing {field} in server {server_info.get('name', 'unknown')}"


def test_server_transport_valid(registry):
    """Verify transport types are valid"""
    valid_transports = ["stdio", "sse", "http"]

    for server in registry["servers"]:
        transport = server["server"]["transport"]
        assert (
            transport in valid_transports
        ), f"Invalid transport {transport} in {server['server']['name']}"


def test_server_version_semver(registry):
    """Verify server versions follow semver"""
    import re

    semver_pattern = r"^[0-9]+\.[0-9]+\.[0-9]+(-[a-z0-9.-]+)?(\+[a-z0-9.-]+)?$"

    for server in registry["servers"]:
        version = server["server"]["version"]
        server_name = server["server"]["name"]
        assert re.match(
            semver_pattern, version
        ), f"Invalid version {version} in {server_name}"


def test_tools_not_empty(registry):
    """Verify each server has at least one tool"""
    for server in registry["servers"]:
        tools = server["tools"]
        server_name = server["server"]["name"]
        assert len(tools) > 0, f"No tools defined for {server_name}"


def test_tool_fields(registry):
    """Verify each tool has required fields"""
    required_fields = ["name", "description", "input_schema"]

    for server in registry["servers"]:
        server_name = server["server"]["name"]
        for tool in server["tools"]:
            for field in required_fields:
                assert (
                    field in tool
                ), f"Missing {field} in tool {tool.get('name', 'unknown')} (server: {server_name})"


def test_metadata_fields(registry):
    """Verify metadata has required fields"""
    required_fields = ["maintainer", "license", "created", "updated"]

    for server in registry["servers"]:
        metadata = server["metadata"]
        server_name = server["server"]["name"]
        for field in required_fields:
            assert field in metadata, f"Missing {field} in metadata for {server_name}"


def test_health_endpoint_format(registry):
    """Verify health endpoints are valid URLs if present"""
    import re

    url_pattern = r"^https?://"

    for server in registry["servers"]:
        if "health" in server and "endpoint" in server["health"]:
            endpoint = server["health"]["endpoint"]
            server_name = server["server"]["name"]
            assert re.match(
                url_pattern, endpoint
            ), f"Invalid health endpoint {endpoint} in {server_name}"


def test_repository_is_github_url(registry):
    """Verify repository URLs are GitHub URLs"""
    import re

    github_pattern = r"^https://github\.com/[^/]+/[^/]+$"

    for server in registry["servers"]:
        repo = server["server"]["repository"]
        server_name = server["server"]["name"]
        assert re.match(
            github_pattern, repo
        ), f"Repository {repo} is not a valid GitHub URL for {server_name}"
