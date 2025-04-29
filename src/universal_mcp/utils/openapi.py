import json
import re
from pathlib import Path
from typing import Any, Dict, List, Literal
from loguru import logger

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from dataclasses import dataclass

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
    else:
        class_name = "APIClient"

    # Collect all methods
    methods = []
    for path, path_info in schema.get("paths", {}).items():
        for method in path_info:
            if method in ["get", "post", "put", "delete", "patch", "options", "head"]:
                operation = path_info[method]
                function = generate_method_code(path, method, operation, schema)
                methods.append(function)

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent.parent / "templates"),
        autoescape=select_autoescape()
    )
    template = env.get_template("api_client.py.j2")

    # Render the template
    class_code = template.render(
        class_name=class_name,
        base_url=base_url,
        methods=methods
    )

    return class_code


@dataclass
class Function:
    name: str
    type: Literal["get", "post", "put", "delete", "patch", "options", "head"]
    args: Dict[str, str]
    return_type: str
    description: str
    tags: List[str]
    implementation: str

    @property
    def args_str(self) -> str:
        """Convert args dictionary to a string representation."""
        return ", ".join(f"{arg}: {typ}" for arg, typ in self.args.items())


def generate_method_code(
    path: str,
    method: str,
    operation: dict[str, Any],
    full_schema: dict[str, Any]
) -> Function:
    """
    Generate a Function object for a single API method.

    Args:
        path: The API path (e.g., '/users/{user_id}').
        method: The HTTP method (e.g., 'get').
        operation: The operation details from the schema.
        full_schema: The complete OpenAPI schema, used for reference resolution.

    Returns:
        A Function object with metadata: name, args, return_type, description, tags.
    """
    logger.debug(f"Generating function for {method.upper()} {path}")

    # Helper to map JSON schema types to Python types
    def map_type(sch: dict[str, Any]) -> str:
        t = sch.get("type")
        if t == "integer":
            return "int"
        if t == "number":
            return "float"
        if t == "boolean":
            return "bool"
        if t == "array":
            return "list[Any]"
        if t == "object":
            return "dict[str, Any]"
        return "Any"


    # Determine function name
    if op_id := operation.get("operationId"):
        cleaned_id = op_id.replace(".", "_").replace("-", "_")
        method_name = convert_to_snake_case(cleaned_id)
    else:
        segments = [seg.replace("-", "_") for seg in path.strip("/").split("/")]
        parts = [method.lower()]
        for seg in segments:
            if seg.startswith("{") and seg.endswith("}"):
                parts.append(f"by_{seg[1:-1]}")
            else:
                parts.append(seg)
        method_name = "_".join(parts)
    logger.debug(f"Resolved function name={method_name}")

    # Resolve references and filter out header params
    resolved_params = []
    for param in operation.get("parameters", []):
        if ref := param.get("$ref"):
            target = resolve_schema_reference(ref, full_schema)
            if target:
                resolved_params.append(target)
            else:
                logger.warning(f"Unresolved parameter reference: {ref}")
        else:
            resolved_params.append(param)

    # Separate params by location
    path_params = [p for p in resolved_params if p.get("in") == "path"]
    query_params = [p for p in resolved_params if p.get("in") == "query"]

    # Analyze requestBody
    has_body = "requestBody" in operation
    body_required = bool(has_body and operation["requestBody"].get("required"))
    content = (operation.get("requestBody", {}) or {}).get("content", {}) if has_body else {}
    is_array_body = False
    request_props: Dict[str, Any] = {}
    required_fields: List[str] = []
    if has_body and content:
        for mime, info in content.items():
            if not mime.startswith("application/json") or "schema" not in info:
                continue
            schema = info["schema"]
            if ref := schema.get("$ref"):
                schema = resolve_schema_reference(ref, full_schema) or schema
            if schema.get("type") == "array":
                is_array_body = True
            else:
                required_fields = schema.get("required", []) or []
                request_props = schema.get("properties", {}) or {}
                for name, prop_schema in list(request_props.items()):
                    if pre := prop_schema.get("$ref"):
                        request_props[name] = resolve_schema_reference(pre, full_schema) or prop_schema

    # Build function arguments with Annotated[type, description]
    arg_defs: Dict[str, str] = {}
    for p in path_params:
        name = p["name"]
        ty = map_type(p.get("schema", {}))
        desc = p.get("description", "")
        arg_defs[name] = f"Annotated[{ty}, {desc!r}]"
    for p in query_params:
        name = p["name"]
        ty = map_type(p.get("schema", {}))
        desc = p.get("description", "")
        if p.get("required"):
            arg_defs[name] = f"Annotated[{ty}, {desc!r}]"
        else:
            arg_defs[name] = f"Annotated[{ty}, {desc!r}] = None"
    if has_body:
        if is_array_body:
            desc = operation["requestBody"].get("description", "")
            if body_required:
                arg_defs["items"] = f"Annotated[list[Any], {desc!r}]"
            else:
                arg_defs["items"] = f"Annotated[list[Any], {desc!r}] = None"
        elif request_props:
            for prop, schema in request_props.items():
                ty = map_type(schema)
                desc = schema.get("description", "")
                if prop in required_fields:
                    arg_defs[prop] = f"Annotated[{ty}, {desc!r}]"
                else:
                    arg_defs[prop] = f"Annotated[{ty}, {desc!r}] = None"
        else:
            desc = operation["requestBody"].get("description", "")
            arg_defs["request_body"] = f"Annotated[Any, {desc!r}] = None"

    # Sort and order arguments
    required_keys = sorted(k for k, v in arg_defs.items() if "=" not in v)
    optional_keys = sorted(k for k, v in arg_defs.items() if "=" in v)
    ordered_args = {k: arg_defs[k] for k in required_keys + optional_keys}

    return_type = determine_return_type(operation)

    # Assemble description
    summary = operation.get("summary", "")
    operation_desc = operation.get("description", "")
    desc_parts: List[str] = []
    if summary:
        desc_parts.append(summary)
    if operation_desc:
        desc_parts.append(operation_desc)
    description_text = ". ".join(desc_parts)

    tags = operation.get("tags", []) or []

    # Generate implementation code
    implementation_lines = []
    
    # Add parameter validation for required fields
    for param in path_params + query_params:
        if param.get("required"):
            name = param["name"]
            implementation_lines.append(f"if {name} is None:")
            implementation_lines.append(f"    raise ValueError(\"Missing required parameter '{name}'\")")
    
    if has_body and body_required:
        if is_array_body:
            implementation_lines.append("if items is None:")
            implementation_lines.append("    raise ValueError(\"Missing required parameter 'items'\")")
        elif request_props:
            for prop in required_fields:
                implementation_lines.append(f"if {prop} is None:")
                implementation_lines.append(f"    raise ValueError(\"Missing required parameter '{prop}'\")")
        else:
            implementation_lines.append("if request_body is None:")
            implementation_lines.append("    raise ValueError(\"Missing required parameter 'request_body'\")")

    # Build request body
    if has_body:
        if is_array_body:
            implementation_lines.append("request_body = items")
        elif request_props:
            implementation_lines.append("request_body = {")
            for prop in request_props:
                implementation_lines.append(f"    \"{prop}\": {prop},")
            implementation_lines.append("}")
            implementation_lines.append("request_body = {k: v for k, v in request_body.items() if v is not None}")
        else:
            implementation_lines.append("request_body = request_body")

    # Build URL with path parameters
    path = "/".join([path_params["name"] for path_params in path_params]) or '\"\"'
    url = '\"{self.base_url}{path}\"'
    implementation_lines.append(f'path = {path}')
    implementation_lines.append(f'url = f{url}')

    # Build query parameters
    if query_params:
        implementation_lines.append("query_params = {")
        for param in query_params:
            name = param["name"]
            implementation_lines.append(f"        \"{name}\": {name},")
        implementation_lines.append("    }")
        implementation_lines.append("query_params = {k: v for k, v in query_params.items() if v is not None}")
    else:
        implementation_lines.append("query_params = {}")

    # Make the request using the appropriate method
    http_method = method.lower()
    if has_body:
        implementation_lines.append(f"response = self._{http_method}(url, data=request_body, params=query_params)")
    else:
        implementation_lines.append(f"response = self._{http_method}(url, params=query_params)")

    # Handle response
    implementation_lines.append("response.raise_for_status()")
    implementation_lines.append("return response.json()")

    implementation = "\n".join(implementation_lines)

    # Build Function object
    function = Function(
        name=method_name,
        type=http_method,
        args=ordered_args,
        return_type=return_type,
        description=description_text,
        tags=tags,
        implementation=implementation
    )

    logger.debug(f"Generated function: {function}")
    return function

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
