import json
from pathlib import Path

import pytest

from universal_mcp.utils.api_generator import generate_api_from_schema


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
    result = await generate_api_from_schema(
        schema_path=sample_schema, output_path=None, add_docstrings=False
    )

    assert "code" in result
    assert isinstance(result["code"], str)
    # Check for required imports
    assert "from universal_mcp.applications import APIApplication" in result["code"]
    assert "from universal_mcp.integrations import Integration" in result["code"]
    # Check for the test operation
    assert "def test_test_operation" in result["code"]
    assert "list_tools" in result["code"]


@pytest.mark.asyncio
async def test_generate_api_with_output(sample_schema, temp_dir):
    """Test API generation with output file."""
    output_path = temp_dir / "test.py"

    result = await generate_api_from_schema(
        schema_path=sample_schema, output_path=output_path, add_docstrings=True
    )

    assert "app_file" in result
    assert "readme_file" in result

    app_file = Path(result["app_file"])
    readme_file = Path(result["readme_file"]) if result["readme_file"] else None

    assert app_file.exists()
    content = app_file.read_text()
    # Check for required imports and class structure
    assert "from universal_mcp.applications import APIApplication" in content
    assert "from universal_mcp.integrations import Integration" in content
    assert "def test_test_operation" in content
    assert "def list_tools" in content

    # Verify README exists and contains expected content
    if readme_file:
        assert readme_file.exists()
        readme_content = readme_file.read_text()
        assert "Test MCP Server" in readme_content
        assert "Tool List" in readme_content
        assert "test_test_operation" in readme_content

    # Verify temporary file was cleaned up
    assert not output_path.exists()


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
        await generate_api_from_schema(
            schema_path=Path("nonexistent.json"), output_path=None
        )


@pytest.mark.asyncio
async def test_generate_api_with_docstrings(sample_schema, temp_dir):
    """Test API generation with docstring generation."""
    output_path = temp_dir / "test_with_docs.py"

    result = await generate_api_from_schema(
        schema_path=sample_schema, output_path=output_path, add_docstrings=True
    )

    app_file = Path(result["app_file"])
    assert app_file.exists()

    # Check if docstrings were added
    content = app_file.read_text()
    # Check for required imports and class structure
    assert "from universal_mcp.applications import APIApplication" in content
    assert "from universal_mcp.integrations import Integration" in content
    assert "def test_test_operation" in content
    assert '"""' in content  # Basic check for docstring presence
    assert "Args:" in content or "Parameters:" in content
    assert "Returns:" in content

    # Verify temporary file was cleaned up
    assert not output_path.exists()


@pytest.mark.asyncio
async def test_generate_api_without_docstrings(sample_schema, temp_dir):
    """Test API generation without docstring generation."""
    output_path = temp_dir / "test_without_docs.py"

    result = await generate_api_from_schema(
        schema_path=sample_schema, output_path=output_path, add_docstrings=False
    )

    app_file = Path(result["app_file"])
    assert app_file.exists()

    # Verify the app was generated
    content = app_file.read_text()
    # Check for required imports and class structure
    assert "from universal_mcp.applications import APIApplication" in content
    assert "from universal_mcp.integrations import Integration" in content
    assert "def test_test_operation" in content
    assert "def list_tools" in content

    # Verify temporary file was cleaned up
    assert not output_path.exists()


def test_applications_directory_structure():
    """Test that the applications directory structure is correct."""
    # Get the applications directory path
    applications_dir = Path(__file__).parent.parent / "universal_mcp" / "applications"

    # Check if applications directory exists
    assert applications_dir.exists()
    assert applications_dir.is_dir()

    # Check if it's a Python package
    assert (applications_dir / "__init__.py").exists()


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
    result = await generate_api_from_schema(
        schema_path=schema_file, output_path=output_path, add_docstrings=True
    )

    app_file = Path(result["app_file"])
    assert app_file.exists()

    content = app_file.read_text()
    # Check for all operations with the 'complex_' prefix
    assert "def complex_list_users" in content
    assert "def complex_create_user" in content
    assert "def complex_get_user" in content

    # Check list_tools includes all operations with proper method references
    assert "self.complex_list_users" in content
    assert "self.complex_create_user" in content
    assert "self.complex_get_user" in content

    # Check for proper class name
    assert "class ComplexApiApp(APIApplication)" in content

    # Check for required imports
    assert "from universal_mcp.applications import APIApplication" in content
    assert "from universal_mcp.integrations import Integration" in content

    # Check for proper typing imports
    assert "from typing import" in content

    # Verify README was generated
    readme_file = Path(result["readme_file"])
    assert readme_file.exists()
    readme_content = readme_file.read_text()

    # Check README content
    assert "Complex MCP Server" in readme_content
    assert "Tool List" in readme_content
    assert "complex_list_users" in readme_content
    assert "complex_create_user" in readme_content
    assert "complex_get_user" in readme_content
