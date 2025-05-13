import json
from pathlib import Path

import pytest

from universal_mcp.utils.openapi.api_generator import generate_api_from_schema


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path


# Fixture for a sample OpenAPI schema
@pytest.fixture
def sample_schema(temp_dir):
    """Create a sample OpenAPI schema file for testing."""
    schema = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/test": {
                "get": {
                    "operationId": "test_operation",
                    "summary": "Test operation",
                    "tags": ["test", "operations"],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"message": {"type": "string"}},
                                    }
                                }
                            },
                        }
                    },
                }
            }
        },
    }

    schema_file = temp_dir / "test_schema.json"
    with open(schema_file, "w") as f:
        json.dump(schema, f)

    return schema_file


@pytest.mark.asyncio
async def test_generate_api_without_output(sample_schema):
    """Test API generation without output file (return code only)."""
    result = generate_api_from_schema(schema_path=sample_schema, output_path=None)

    assert "code" in result
    assert isinstance(result["code"], str)
    # Check for required imports
    assert "from universal_mcp.applications import APIApplication" in result["code"]
    assert "from universal_mcp.integrations import Integration" in result["code"]
    # Check for the test operation (now without prefix)
    assert "def test_operation" in result["code"]
    assert "list_tools" in result["code"]


@pytest.mark.asyncio
async def test_generate_api_with_output(sample_schema, temp_dir):
    """Test API generation with output file."""
    output_path = temp_dir / "test.py"

    app_file = generate_api_from_schema(schema_path=sample_schema, output_path=output_path)

    assert "app_file" != None
    assert "readme_file" != None

    assert app_file.exists()
    content = app_file.read_text()
    # Check for required imports and class structure
    assert "from universal_mcp.applications import APIApplication" in content
    assert "from universal_mcp.integrations import Integration" in content
    assert "def test_operation" in content
    assert "def list_tools" in content


@pytest.mark.asyncio
async def test_generate_api_invalid_schema(temp_dir):
    """Test API generation with invalid schema."""
    invalid_schema = temp_dir / "invalid_schema.json"
    with open(invalid_schema, "w") as f:
        f.write("invalid json")
    with pytest.raises(json.JSONDecodeError):
        await generate_api_from_schema(schema_path=invalid_schema, output_path=None)


@pytest.mark.asyncio
async def test_generate_api_nonexistent_schema():
    """Test API generation with nonexistent schema file."""
    with pytest.raises(FileNotFoundError):
        await generate_api_from_schema(schema_path=Path("nonexistent.json"), output_path=None)


@pytest.mark.asyncio
async def test_generate_api_without_docstrings(sample_schema, temp_dir):
    """Test API generation without docstring generation."""
    output_path = temp_dir / "test_without_docs.py"

    app_file = generate_api_from_schema(schema_path=sample_schema, output_path=output_path)

    assert app_file is not None
    assert app_file.exists()

    # Verify the app was generated
    content = app_file.read_text()
    # Check for required imports and class structure
    assert "from universal_mcp.applications import APIApplication" in content
    assert "from universal_mcp.integrations import Integration" in content
    assert "def test_operation" in content
    assert "def list_tools" in content


@pytest.mark.asyncio
async def test_generate_api_with_complex_schema(temp_dir):
    """Test API generation with a more complex schema including multiple operations."""
    # Create a more complex schema with multiple operations
    schema = {
        "openapi": "3.0.0",
        "info": {"title": "Complex API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "list_users",
                    "summary": "List all users",
                    "responses": {"200": {"description": "Success"}},
                },
                "post": {
                    "operationId": "create_user",
                    "summary": "Create a user",
                    "responses": {"201": {"description": "Created"}},
                },
            },
            "/users/{id}": {
                "get": {
                    "operationId": "get_user",
                    "summary": "Get user by ID",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "Success"}},
                }
            },
        },
    }

    schema_file = temp_dir / "complex_schema.json"
    with open(schema_file, "w") as f:
        json.dump(schema, f)

    output_path = temp_dir / "complex.py"
    app_file = generate_api_from_schema(schema_path=schema_file, output_path=output_path)

    assert app_file is not None
    assert app_file.exists()

    content = app_file.read_text()
    # Check for all operations (without the 'complex_' prefix)
    assert "def list_users" in content
    assert "def create_user" in content
    assert "def get_user" in content

    # Check list_tools includes all operations with proper method references
    assert "self.list_users" in content
    assert "self.create_user" in content
    assert "self.get_user" in content

    # Check for proper class name
    assert "class ComplexApiApp(APIApplication)" in content

    # Check for required imports
    assert "from universal_mcp.applications import APIApplication" in content
    assert "from universal_mcp.integrations import Integration" in content

    # Check for proper typing imports
    assert "from typing import" in content
