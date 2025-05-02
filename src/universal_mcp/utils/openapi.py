import json
import re
from pathlib import Path
from typing import Any, Literal

from jsonref import replace_refs

import yaml
from pydantic import BaseModel


class Parameters(BaseModel):
    name: str
    identifier: str
    description: str = ""
    type: str = "string"
    where: Literal["path", "query", "header", "body"]
    required: bool
    example: str | None = None

    def __str__(self):
        return f"{self.name}: ({self.type})"


class Method(BaseModel):
    name: str
    summary: str
    tags: list[str]
    path: str
    method: str
    path_params: list[Parameters]
    query_params: list[Parameters]
    body_params: list[Parameters]
    return_type: str

    def deduplicate_params(self):
        """
        Deduplicate parameters by name.
        Sometimes the same parameter is defined in multiple places, we only want to include it once.
        """
        # TODO: Implement this
        pass

    def render(self, template_dir: str, template_name: str = "method.jinja2") -> str:
        """
        Render this Method instance into source code using a Jinja2 template.

        Args:
            template_dir (str): Directory where the Jinja2 templates are located.
            template_name (str): Filename of the method template.

        Returns:
            str: The rendered method source code.
        """
        from jinja2 import Environment, FileSystemLoader

        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template(template_name)
        return template.render(method=self)


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


def _extract_properties_from_schema(schema: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Extracts properties and required fields from a schema, handling 'allOf'."""
    properties = {}
    required_fields = []

    if 'allOf' in schema:
        for sub_schema in schema['allOf']:
            sub_props, sub_required = _extract_properties_from_schema(sub_schema)
            properties.update(sub_props)
            required_fields.extend(sub_required)
    
    # Combine with top-level properties and required fields, if any
    properties.update(schema.get('properties', {}))
    required_fields.extend(schema.get('required', []))
    
    # Deduplicate required fields
    required_fields = list(set(required_fields))
    
    return properties, required_fields


def _load_and_resolve_references(path: Path):
    # Load the schema
    type = "yaml" if path.suffix == ".yaml" else "json"
    with open(path) as f:
        schema = yaml.safe_load(f) if type == "yaml" else json.load(f)
    # Resolve references
    return replace_refs(schema)


def _determine_return_type(operation: dict[str, Any]) -> str:
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


def _determine_function_name(operation: dict[str, Any], path: str, method: str) -> str:
    """
    Determine the function name from the operation.
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
    return func_name


def _generate_path_params(path: str) -> list[Parameters]:
    path_params_in_url = re.findall(r"{([^}]+)}", path)
    parameters = []
    for param in path_params_in_url:
        try:
            parameters.append(
                Parameters(
                    name=param.replace("-", "_"),
                    identifier=param,
                    description=param,
                    type="string",
                    where="path",
                    required=True,
                )
            )
        except Exception as e:
            print(f"Error generating path parameters {param}: {e}")
            raise e
    return parameters


def _generate_url(path: str, path_params: list[Parameters]):
    formatted_path = path
    for param in path_params:
        formatted_path = formatted_path.replace(
            f"{{{param.identifier}}}", f"{{{param.name}}}"
        )
    return formatted_path


def _generate_query_params(operation: dict[str, Any]) -> list[Parameters]:
    query_params = []
    for param in operation.get("parameters", []):
        name = param.get("name")
        if name is None:
            continue
            
        # Clean the parameter name for use as a Python identifier
        clean_name = name.replace("-", "_").replace(".", "_").replace("[", "_").replace("]", "")
        
        description = param.get("description", "")
        
        # Extract type from schema if available
        param_schema = param.get("schema", {})
        type_value = param_schema.get("type") if param_schema else param.get("type")
        # Default to string if type is not available
        if type_value is None:
            type_value = "string"
            
        where = param.get("in")
        required = param.get("required", False)
        if where == "query":
            parameter = Parameters(
                name=clean_name,
                identifier=name,
                description=description,
                type=type_value,
                where=where,
                required=required,
            )
            query_params.append(parameter)
    return query_params


def _generate_body_params(operation: dict[str, Any]) -> list[Parameters]:
    body_params = []
    request_body = operation.get("requestBody", {})
    if not request_body:
        return [] # No request body defined
        
    required_body = request_body.get("required", False)
    content = request_body.get("content", {})
    json_content = content.get("application/json", {})
    if not json_content or "schema" not in json_content:
        return [] # No JSON schema found
        
    schema = json_content.get("schema", {})
    properties, required_fields = _extract_properties_from_schema(schema)

    for param_name, param_schema in properties.items():
        param_type = param_schema.get("type", "string")
        param_description = param_schema.get("description", param_name)
        # Parameter is required if the body is required AND the field is in the schema's required list
        param_required = required_body and param_name in required_fields 
        body_params.append(
            Parameters(
                name=param_name.replace("-", "_").replace(".", "_").replace("[", "_").replace("]", ""), # Clean name for Python
                identifier=param_name, # Original name for API
                description=param_description,
                type=param_type,
                where="body",
                required=param_required,
            )
        )
    return body_params


def _generate_method_code(path, method, operation):
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

    func_name = _determine_function_name(operation, path, method)
    operation.get("summary", "")
    operation.get("tags", [])
    # Extract path parameters from the URL path
    path_params = _generate_path_params(path)
    query_params = _generate_query_params(operation)
    _generate_body_params(operation)
    return_type = _determine_return_type(operation)
    # gen_method   = Method(name=func_name, summary=summary, tags=tags, path=path, method=method, path_params=path_params, query_params=query_params, body_params=body_params, return_type=return_type)
    # logger.info(f"Generated method: {gen_method.model_dump()}")
    # return method.render(template_dir="templates", template_name="method.jinja2")

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

                    # Check if properties is empty and additionalProperties is true
                    if (
                        schema.get("type") == "object"
                        and schema.get("additionalProperties", False) is True
                    ):
                        properties = schema.get("properties", {})
                        if not properties or len(properties) == 0:
                            has_empty_body = True

    # Extract request body schema properties and required fields
    request_body_properties = {}
    required_fields = []
    is_array_body = False

    if has_body:
        request_body_content = operation.get("requestBody", {}).get("content", {})
        json_content = request_body_content.get("application/json", {})
        if json_content and "schema" in json_content:
            schema = json_content["schema"]
            if schema.get("type") == "array":
                is_array_body = True
            else:
                # Use the helper function to extract properties and required fields
                request_body_properties, required_fields = _extract_properties_from_schema(schema)
                # Handle schemas with empty properties but additionalProperties: true
                if (not request_body_properties or len(request_body_properties) == 0) and schema.get("additionalProperties") is True:
                    has_empty_body = True

    # Build function arguments
    required_args = []
    optional_args = []

    # Add path parameters
    for param in path_params:
        if param.name not in required_args:
            required_args.append(param.name)

    for param in query_params:
        param_name = param.name
        # Handle parameters with square brackets and hyphens by converting to valid Python identifiers
        param_identifier = (
            param_name.replace("[", "_").replace("]", "").replace("-", "_")
        )
        if param_identifier not in required_args and param_identifier not in [
            p.split("=")[0] for p in optional_args
        ]:
            if param.required:
                required_args.append(param_identifier)
            else:
                optional_args.append(f"{param_identifier}=None")

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
                prop_schema = request_body_properties[prop_name]
                clean_prop_name = prop_name.replace("-", "_").replace(".", "_").replace("[", "_").replace("]", "")
                
                if prop_name in required_fields:
                    request_body_params.append(clean_prop_name)
                    if clean_prop_name not in required_args:
                        required_args.append(clean_prop_name)
                else:
                    request_body_params.append(clean_prop_name)
                    # Handle optional parameters with defaults
                    default_value = prop_schema.get("default")
                    arg_str = f"{clean_prop_name}=None"
                    if default_value is not None:
                        # Format default value for Python signature
                        if isinstance(default_value, str):
                            formatted_default = f'"{repr(default_value)[1:-1]}"' # Use repr() and slice to handle internal quotes
                        elif isinstance(default_value, bool):
                            formatted_default = str(default_value) # True/False becomes "True"/"False"
                        elif isinstance(default_value, (int, float)):
                            formatted_default = str(default_value) # Numbers as strings
                        else:
                            formatted_default = "None"
                        arg_str = f"{clean_prop_name}={formatted_default}"
                        
                    if arg_str not in optional_args:
                        optional_args.append(arg_str)

    # If request body is present but empty (content: {}), add a generic request_body parameter
    if has_empty_body and "request_body=None" not in optional_args:
        optional_args.append("request_body=None")

    # Combine required and optional arguments
    args = required_args + optional_args

    # Determine return type
    return_type = _determine_return_type(operation)
    if args:
        signature = f"    def {func_name}(self, {', '.join(args)}) -> {return_type}:"
    else:
        signature = f"    def {func_name}(self) -> {return_type}:"

    # Build method body
    body_lines = []

    for param in path_params:
        body_lines.append(f"        if {param.name} is None:")
        body_lines.append(
            f"            raise ValueError(\"Missing required parameter '{param.identifier}'\")"  # Use original name in error
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
    url = _generate_url(path, path_params)
    url_line = f'        url = f"{{self.base_url}}{url}"'
    body_lines.append(url_line)

    # Build query parameters, handling square brackets in parameter names
    if query_params:
        query_params_items = []
        for param in query_params:
            param_name = param.identifier
            param_identifier = (
                param.name.replace("[", "_").replace("]", "").replace("-", "_")
            )
            query_params_items.append(f"('{param_name}', {param_identifier})")
        body_lines.append(
            f"        query_params = {{k: v for k, v in [{', '.join(query_params_items)}] if v is not None}}"
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


def load_schema(path: Path):
    return _load_and_resolve_references(path)


def generate_api_client(schema, class_name: str | None = None):
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
        if class_name:
            clean_name = (
                class_name.capitalize()[:-3]
                if class_name.endswith("App")
                else class_name.capitalize()
            )
        else:
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
                method_code, func_name = _generate_method_code(path, method, operation)
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
