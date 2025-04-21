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
        str: The appropriate return type annotation (list[Any], dict[str, Any], or Any)
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
                    return "list[Any]"
                elif schema.get("type") == "object" or "$ref" in schema:
                    return "dict[str, Any]"

    # Default to Any if unable to determine
    return "Any"


def resolve_schema_reference(reference, schema):
    """
    Resolve a JSON schema reference to its target schema.

    Args:
        reference (str): The reference string (e.g., '#/components/schemas/User')
        schema (dict): The complete OpenAPI schema that contains the reference

    Returns:
        dict: The resolved schema, or None if not found
    """
    if not reference.startswith("#/"):
        return None

    # Split the reference path and navigate through the schema
    parts = reference[2:].split("/")
    current = schema

    for part in parts:
        if part in current:
            current = current[part]
        else:
            return None

    return current


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
                    path, method, operation, schema, tool_name
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
        "from typing import Any",
        "from universal_mcp.applications import APIApplication",
        "from universal_mcp.integrations import Integration",
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


def generate_method_code(path, method, operation, full_schema, tool_name=None):
    """
    Generate the code for a single API method.

    Args:
        path (str): The API path (e.g., '/users/{user_id}').
        method (str): The HTTP method (e.g., 'get').
        operation (dict): The operation details from the schema.
        full_schema (dict): The complete OpenAPI schema, used for reference resolution.
        tool_name (str, optional): The name of the tool/app to prefix the function name with.

    Returns:
        tuple: (method_code, func_name) - The Python code for the method and its name.
    """
    # Extract path parameters from the URL path
    path_params_in_url = re.findall(r"{([^}]+)}", path)

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

    # Only fix isolated 'a' and 'an' as articles, not when they're part of words
    func_name = re.sub(
        r"_a([^_a-z])", r"_a_\1", func_name
    )  # Fix for patterns like retrieve_ablock -> retrieve_a_block
    func_name = re.sub(
        r"_a$", r"_a", func_name
    )  # Don't change if 'a' is at the end of the name
    func_name = re.sub(
        r"_an([^_a-z])", r"_an_\1", func_name
    )  # Fix for patterns like create_anitem -> create_an_item
    func_name = re.sub(
        r"_an$", r"_an", func_name
    )  # Don't change if 'an' is at the end of the name

    # Get parameters and request body
    # Resolve parameter references before processing
    resolved_parameters = []
    for param in operation.get("parameters", []):
        if "$ref" in param:
            # Resolve reference to actual parameter object
            ref_param = resolve_schema_reference(param["$ref"], full_schema)
            if ref_param:
                resolved_parameters.append(ref_param)
            else:
                print(
                    f"Warning: Could not resolve parameter reference: {param['$ref']}"
                )
        else:
            resolved_parameters.append(param)

    # Filter out header parameters from the resolved parameters
    parameters = [param for param in resolved_parameters if param.get("in") != "header"]

    has_body = "requestBody" in operation
    body_required = has_body and operation["requestBody"].get("required", False)

    # Check if the requestBody has actual content or is empty
    has_empty_body = False
    if has_body:
        request_body_content = operation["requestBody"].get("content", {})
        if not request_body_content or all(
            not content for content_type, content in request_body_content.items()
        ):
            has_empty_body = True
        else:
            # Handle empty properties with additionalProperties:true
            for content_type, content in request_body_content.items():
                if content_type.startswith("application/json") and "schema" in content:
                    schema = content["schema"]

                    # Resolve schema reference if present
                    if "$ref" in schema:
                        ref_schema = resolve_schema_reference(
                            schema["$ref"], full_schema
                        )
                        if ref_schema:
                            schema = ref_schema

                    # Check if properties is empty and additionalProperties is true
                    if (
                        schema.get("type") == "object"
                        and schema.get("additionalProperties", False) is True
                    ):
                        properties = schema.get("properties", {})
                        if not properties or len(properties) == 0:
                            has_empty_body = True

    # Extract request body schema properties and required fields
    required_fields = []
    request_body_properties = {}
    is_array_body = False
    array_items_schema = None

    if has_body:
        for content_type, content in (
            operation["requestBody"].get("content", {}).items()
        ):
            if content_type.startswith("application/json") and "schema" in content:
                schema = content["schema"]

                # Resolve schema reference if present
                if "$ref" in schema:
                    ref_schema = resolve_schema_reference(schema["$ref"], full_schema)
                    if ref_schema:
                        schema = ref_schema

                # Check if the schema is an array type
                if schema.get("type") == "array":
                    is_array_body = True
                    array_items_schema = schema.get("items", {})
                    # Try to resolve any reference in items
                    if "$ref" in array_items_schema:
                        array_items_schema = resolve_schema_reference(
                            array_items_schema["$ref"], full_schema
                        )
                else:
                    # Extract required fields from schema
                    if "required" in schema:
                        required_fields = schema["required"]
                    # Extract properties from schema
                    if "properties" in schema:
                        request_body_properties = schema["properties"]

                        # Check for nested references in properties
                        for prop_name, prop_schema in request_body_properties.items():
                            if "$ref" in prop_schema:
                                ref_prop_schema = resolve_schema_reference(
                                    prop_schema["$ref"], full_schema
                                )
                                if ref_prop_schema:
                                    request_body_properties[prop_name] = ref_prop_schema

                # Handle schemas with empty properties but additionalProperties: true
                # by treating them similar to empty bodies
                if (
                    not request_body_properties or len(request_body_properties) == 0
                ) and schema.get("additionalProperties") is True:
                    has_empty_body = True

    # Build function arguments
    required_args = []
    optional_args = []

    # Add path parameters
    for param_name in path_params_in_url:
        if param_name not in required_args:
            required_args.append(param_name)

    # Add query parameters
    for param in parameters:
        param_name = param["name"]
        if param_name not in required_args:
            if param.get("required", False):
                required_args.append(param_name)
            else:
                optional_args.append(f"{param_name}=None")

    # Handle array type request body differently
    request_body_params = []
    if has_body:
        if is_array_body:
            # For array request bodies, add a single parameter for the entire array
            array_param_name = "items"
            # Try to get a better name from the operation or path
            if func_name.endswith("_list_input"):
                array_param_name = func_name.replace("_list_input", "")
            elif "List" in func_name:
                array_param_name = func_name.split("List")[0].lower() + "_list"

            # Make the array parameter required if the request body is required
            if body_required:
                required_args.append(array_param_name)
            else:
                optional_args.append(f"{array_param_name}=None")

            # Remember this is an array param
            request_body_params = [array_param_name]
        elif request_body_properties:
            # For object request bodies, add individual properties as parameters
            for prop_name in request_body_properties:
                if prop_name in required_fields:
                    request_body_params.append(prop_name)
                    if prop_name not in required_args:
                        required_args.append(prop_name)
                else:
                    request_body_params.append(prop_name)
                    if f"{prop_name}=None" not in optional_args:
                        optional_args.append(f"{prop_name}=None")

    # If request body is present but empty (content: {}), add a generic request_body parameter
    if has_empty_body and "request_body=None" not in optional_args:
        optional_args.append("request_body=None")

    # Combine required and optional arguments
    args = required_args + optional_args

    # Determine return type
    return_type = determine_return_type(operation)

    signature = f"    def {func_name}(self, {', '.join(args)}) -> {return_type}:"

    # Build method body
    body_lines = []

    # Validate required parameters including path parameters
    for param_name in required_args:
        body_lines.append(f"        if {param_name} is None:")
        body_lines.append(
            f"            raise ValueError(\"Missing required parameter '{param_name}'\")"
        )

    # Build request body (handle array and object types differently)
    if has_body:
        if is_array_body:
            # For array request bodies, use the array parameter directly
            body_lines.append("        # Use items array directly as request body")
            body_lines.append(f"        request_body = {request_body_params[0]}")
        elif request_body_properties:
            # For object request bodies, build the request body from individual parameters

            body_lines.append("        request_body = {")

            for prop_name in request_body_params:
                # Only include non-None values in the request body
                body_lines.append(f"            '{prop_name}': {prop_name},")

            body_lines.append("        }")

            body_lines.append(
                "        request_body = {k: v for k, v in request_body.items() if v is not None}"
            )

    # Format URL directly with path parameters
    url_line = f'        url = f"{{self.base_url}}{path}"'
    body_lines.append(url_line)

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

    # Make HTTP request using the proper method
    method_lower = method.lower()

    # Determine what to use as the request body argument
    if has_empty_body:
        request_body_arg = "request_body"
    elif not has_body:
        request_body_arg = "{}"
    else:
        request_body_arg = "request_body"

    if method_lower == "get":
        body_lines.append("        response = self._get(url, params=query_params)")
    elif method_lower == "post":
        body_lines.append(
            f"        response = self._post(url, data={request_body_arg}, params=query_params)"
        )
    elif method_lower == "put":
        body_lines.append(
            f"        response = self._put(url, data={request_body_arg}, params=query_params)"
        )
    elif method_lower == "patch":
        body_lines.append(
            f"        response = self._patch(url, data={request_body_arg}, params=query_params)"
        )
    elif method_lower == "delete":
        body_lines.append("        response = self._delete(url, params=query_params)")
    else:
        body_lines.append(
            f"        response = self._{method_lower}(url, data={request_body_arg}, params=query_params)"
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
