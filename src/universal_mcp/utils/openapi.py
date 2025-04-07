import json
import re
from pathlib import Path
from typing import Any

import yaml


def convert_to_snake_case(identifier: str) -> str:
    """
    Convert a camelCase or PascalCase identifier to snake_case.

    Args:
        identifier (str): The string to convert

    Returns:
        str: The converted snake_case string
    """
    if not identifier:
        return identifier
    # Add underscore between lowercase and uppercase letters
    result = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", identifier)
    # Convert to lowercase
    return result.lower()


def load_schema(path: Path):
    type = "yaml" if path.suffix == ".yaml" else "json"
    with open(path) as f:
        if type == "yaml":
            return yaml.safe_load(f)
        else:
            return json.load(f)


def determine_return_type(operation: dict[str, Any]) -> str:
    """
    Determine the return type from the response schema.

    Args:
        operation (dict): The operation details from the schema.

    Returns:
        str: The appropriate return type annotation (List[Any], Dict[str, Any], or Any)
    """
    responses = operation.get("responses", {})
    # Find successful response (2XX)
    success_response = None
    for code in responses:
        if code.startswith("2"):
            success_response = responses[code]
            break

    if not success_response:
        return "Any"  # Default to Any if no success response

    # Check if there's content with schema
    if "content" in success_response:
        for content_type, content_info in success_response["content"].items():
            if content_type.startswith("application/json") and "schema" in content_info:
                schema = content_info["schema"]

                # Only determine if it's a list, dict, or unknown (Any)
                if schema.get("type") == "array":
                    return "List[Any]"
                elif schema.get("type") == "object" or "$ref" in schema:
                    return "Dict[str, Any]"

    # Default to Any if unable to determine
    return "Any"


def generate_api_client(schema):
    """
    Generate a Python API client class from an OpenAPI schema.

    Args:
        schema (dict): The OpenAPI schema as a dictionary.

    Returns:
        str: A string containing the Python code for the API client class.
    """
    methods = []
    method_names = []

    # Extract API info for naming and base URL
    info = schema.get("info", {})
    api_title = info.get("title", "API")

    # Get base URL from servers array if available
    base_url = ""
    servers = schema.get("servers", [])
    if servers and isinstance(servers, list) and "url" in servers[0]:
        base_url = servers[0]["url"].rstrip("/")

    # Create a clean class name from API title
    if api_title:
        # Convert API title to a clean class name
        base_name = "".join(word.capitalize() for word in api_title.split())
        clean_name = "".join(c for c in base_name if c.isalnum())
        class_name = f"{clean_name}App"

        # Extract tool name - remove spaces and convert to lowercase
        tool_name = api_title.lower()

        # Remove version numbers (like 3.0, v1, etc.)
        tool_name = re.sub(r"\s*v?\d+(\.\d+)*", "", tool_name)

        # Remove common words that aren't needed
        common_words = ["api", "openapi", "open", "swagger", "spec", "specification"]
        for word in common_words:
            tool_name = tool_name.replace(word, "")

        # Remove spaces, hyphens, underscores
        tool_name = tool_name.replace(" ", "").replace("-", "").replace("_", "")

        # Remove any non-alphanumeric characters
        tool_name = "".join(c for c in tool_name if c.isalnum())

        # If empty (after cleaning), use generic name
        if not tool_name:
            tool_name = "api"
    else:
        class_name = "APIClient"
        tool_name = "api"

    # Iterate over paths and their operations
    for path, path_info in schema.get("paths", {}).items():
        for method in path_info:
            if method in ["get", "post", "put", "delete", "patch", "options", "head"]:
                operation = path_info[method]
                method_code, func_name = generate_method_code(
                    path, method, operation, tool_name
                )
                methods.append(method_code)
                method_names.append(func_name)

    # Generate list_tools method with all the function names
    tools_list = ",\n            ".join([f"self.{name}" for name in method_names])
    list_tools_method = f"""    def list_tools(self):
        return [
            {tools_list}
        ]"""

    # Generate class imports
    imports = [
        "from universal_mcp.applications import APIApplication",
        "from universal_mcp.integrations import Integration",
        "from typing import Any, Dict, List",
    ]

    # Construct the class code
    class_code = (
        "\n".join(imports) + "\n\n"
        f"class {class_name}(APIApplication):\n"
        f"    def __init__(self, integration: Integration = None, **kwargs) -> None:\n"
        f"        super().__init__(name='{class_name.lower()}', integration=integration, **kwargs)\n"
        f'        self.base_url = "{base_url}"\n\n'
        + "\n\n".join(methods)
        + "\n\n"
        + list_tools_method
        + "\n"
    )
    return class_code


def generate_method_code(path, method, operation, tool_name=None):
    """
    Generate the code for a single API method.

    Args:
        path (str): The API path (e.g., '/users/{user_id}').
        method (str): The HTTP method (e.g., 'get').
        operation (dict): The operation details from the schema.
        tool_name (str, optional): The name of the tool/app to prefix the function name with.

    Returns:
        tuple: (method_code, func_name) - The Python code for the method and its name.
    """
    # Determine function name
    if "operationId" in operation:
        raw_name = operation["operationId"]
        cleaned_name = raw_name.replace(".", "_").replace("-", "_")
        func_name = convert_to_snake_case(cleaned_name)
    else:
        # Generate name from path and method
        path_parts = path.strip("/").split("/")
        name_parts = [method]
        for part in path_parts:
            if part.startswith("{") and part.endswith("}"):
                name_parts.append("by_" + part[1:-1])
            else:
                name_parts.append(part)
        func_name = "_".join(name_parts).replace("-", "_").lower()

    # Add tool name prefix if provided
    if tool_name:
        func_name = f"{tool_name}_{func_name}"

    # Get parameters and request body
    parameters = operation.get("parameters", [])
    has_body = "requestBody" in operation
    body_required = has_body and operation["requestBody"].get("required", False)

    # Build function arguments
    required_args = []
    optional_args = []
    for param in parameters:
        if param.get("required", False):
            required_args.append(param["name"])
        else:
            optional_args.append(f"{param['name']}=None")

    # Add request body parameter
    if has_body:
        if body_required:
            required_args.append("request_body")
        else:
            optional_args.append("request_body=None")

    # Combine required and optional arguments
    args = required_args + optional_args

    # Determine return type
    return_type = determine_return_type(operation)

    signature = f"    def {func_name}(self, {', '.join(args)}) -> {return_type}:"

    # Build method body
    body_lines = []

    # Validate required parameters
    for param in parameters:
        if param.get("required", False):
            body_lines.append(f"        if {param['name']} is None:")
            body_lines.append(
                f"            raise ValueError(\"Missing required parameter '{param['name']}'\")"
            )

    # Validate required body
    if has_body and body_required:
        body_lines.append("        if request_body is None:")
        body_lines.append(
            '            raise ValueError("Missing required request body")'
        )

    # Path parameters
    path_params = [p for p in parameters if p["in"] == "path"]
    path_params_dict = ", ".join([f"'{p['name']}': {p['name']}" for p in path_params])
    body_lines.append(f"        path_params = {{{path_params_dict}}}")

    # Format URL
    body_lines.append(
        f'        url = f"{{self.base_url}}{path}".format_map(path_params)'
    )

    # Query parameters
    query_params = [p for p in parameters if p["in"] == "query"]
    if query_params:
        query_params_items = ", ".join(
            [f"('{p['name']}', {p['name']})" for p in query_params]
        )
        body_lines.append(
            f"        query_params = {{k: v for k, v in [{query_params_items}] if v is not None}}"
        )
    else:
        body_lines.append("        query_params = {}")

    # Request body handling for JSON
    if has_body:
        body_lines.append(
            "        json_body = request_body if request_body is not None else None"
        )

    # Make HTTP request using the proper method
    method_lower = method.lower()
    if method_lower == "get":
        body_lines.append("        response = self._get(url, params=query_params)")
    elif method_lower == "post":
        if has_body:
            body_lines.append(
                "        response = self._post(url, data=json_body, params=query_params)"
            )
        else:
            body_lines.append(
                "        response = self._post(url, data={}, params=query_params)"
            )
    elif method_lower == "put":
        if has_body:
            body_lines.append(
                "        response = self._put(url, data=json_body, params=query_params)"
            )
        else:
            body_lines.append(
                "        response = self._put(url, data={}, params=query_params)"
            )
    elif method_lower == "delete":
        body_lines.append("        response = self._delete(url, params=query_params)")
    else:
        body_lines.append(
            f"        response = self._{method_lower}(url, data={{}}, params=query_params)"
        )

    # Handle response
    body_lines.append("        response.raise_for_status()")
    body_lines.append("        return response.json()")

    method_code = signature + "\n" + "\n".join(body_lines)
    return method_code, func_name


# Example usage
if __name__ == "__main__":
    # Sample OpenAPI schema
    schema = {
        "paths": {
            "/users": {
                "get": {
                    "summary": "Get a list of users",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "A list of users",
                            "content": {
                                "application/json": {"schema": {"type": "array"}}
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Create a user",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"name": {"type": "string"}},
                                }
                            }
                        },
                    },
                    "responses": {"201": {"description": "User created"}},
                },
            },
            "/users/{user_id}": {
                "get": {
                    "summary": "Get a user by ID",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "User details"}},
                }
            },
        }
    }

    schema = load_schema("openapi.yaml")
    code = generate_api_client(schema)
    print(code)
