import json
import re
import textwrap
from pathlib import Path
from typing import Any, Literal

import yaml
from jsonref import replace_refs
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


def _sanitize_identifier(name: str | None) -> str:
    """Cleans a string to be a valid Python identifier.

    Replaces hyphens, dots, and square brackets with underscores.
    Removes closing square brackets.
    Returns empty string if input is None.
    """
    if name is None:
        return ""
    return name.replace("-", "_").replace(".", "_").replace("[", "_").replace("]", "")


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
    for param_name in path_params_in_url:

        try:
            parameters.append(
                Parameters(
                    name=_sanitize_identifier(param_name),
                    identifier=param_name,
                    description=param_name, 
                    type="string", 
                    where="path",
                    required=True, 
                    example=None 
                )
            )
        except Exception as e:
            print(f"Error generating path parameters {param_name}: {e}")
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
        clean_name = _sanitize_identifier(name)
        
        description = param.get("description", "")
        
        # Extract type from schema if available
        param_schema = param.get("schema", {})
        type_value = param_schema.get("type") if param_schema else param.get("type")
        # Default to string if type is not available
        if type_value is None:
            type_value = "string"
            
        # Extract example
        example_value = param.get("example", param_schema.get("example"))
        
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
                example=str(example_value) if example_value is not None else None 
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
        # Extract example
        param_example = param_schema.get("example")
        
        body_params.append(
            Parameters(
                name=_sanitize_identifier(param_name), # Clean name for Python
                identifier=param_name, # Original name for API
                description=param_description,
                type=param_type,
                where="body",
                required=param_required,
                example=str(param_example) if param_example is not None else None 
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
    body_params = _generate_body_params(operation)
    return_type = _determine_return_type(operation)
    
    has_body = "requestBody" in operation
    body_required = has_body and operation["requestBody"].get("required", False)
    has_empty_body = False
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
                request_body_properties, required_fields = _extract_properties_from_schema(schema)
                if (not request_body_properties or len(request_body_properties) == 0) and schema.get("additionalProperties") is True:
                    has_empty_body = True
        elif not request_body_content or all(not c for _, c in request_body_content.items()): # Check if content is truly empty
             has_empty_body = True

    # Build function arguments with deduplication (Priority: Path > Body > Query)
    required_args = []
    optional_args = []
    seen_clean_names = set() # Keep track of names added to the signature - DEFINED HERE NOW

    # 1. Process Path Parameters (Highest Priority)
    for param in path_params:
        if param.name not in required_args:
            required_args.append(param.name)
        seen_clean_names.add(param.name)

    for param in query_params:
        
        param_identifier_for_signature = param.name # Use the cleaned name for signature
        if param_identifier_for_signature not in required_args and param_identifier_for_signature not in [
            p.split("=")[0] for p in optional_args
        ]:
            if param.required:
                required_args.append(param_identifier_for_signature)
            else:
                optional_args.append(f"{param_identifier_for_signature}=None")
        seen_clean_names.add(param.name)

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
                # Clean the original prop_name for Python identifier using the helper
                clean_prop_name = _sanitize_identifier(prop_name) 
                
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
                        elif isinstance(default_value, int | float):
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

    # ----- Build Docstring ----- 
    docstring_parts = []
    return_type = _determine_return_type(operation) 
    
    # Summary
    summary = operation.get("summary", "").strip()
    if not summary:
        summary = operation.get("description", f"Execute {method.upper()} {path}").strip()
        summary = summary.split('\n')[0]
    if summary:
        docstring_parts.append(summary)
    
    # Args
    args_doc_lines = []
    param_details = {}
    all_params = path_params + query_params + body_params
    signature_arg_names = {a.split('=')[0] for a in args} 

    for param in all_params:
        if param.name in signature_arg_names and param.name not in param_details:
            param_details[param.name] = param
            
    # Fetch request body example 
    request_body_example_str = None
    if has_body:
        try:
            json_content = operation['requestBody']['content']['application/json']
            example_data = None
            if 'example' in json_content:
                example_data = json_content['example']
            elif 'examples' in json_content and json_content['examples']:
                first_example_key = list(json_content['examples'].keys())[0]
                example_data = json_content['examples'][first_example_key].get('value')

            if example_data is not None:
                try:
                    example_json = json.dumps(example_data, indent=2)
                    indented_example = textwrap.indent(example_json, ' ' * 8) # 8 spaces
                    request_body_example_str = f"\n        Example:\n        ```json\n{indented_example}\n        ```"
                except TypeError:
                    request_body_example_str = f"\n        Example: {example_data}"
        except KeyError:
            pass # No example found

    # Identify the last argument related to the request body
    last_body_arg_name = None
    # request_body_params contains the names as they appear in the signature
    if request_body_params:
        # Find which of these appears last in the combined args list
        body_args_in_signature = [a.split('=')[0] for a in args if a.split('=')[0] in request_body_params]
        if body_args_in_signature:
            last_body_arg_name = body_args_in_signature[-1]

    if signature_arg_names:
        args_doc_lines.append("Args:")
        for arg_signature_str in args:
            arg_name = arg_signature_str.split('=')[0]
            example_str = None # Initialize example_str here
            detail = param_details.get(arg_name)
            if detail:
                desc = detail.description or "No description provided."
                type_hint = detail.type if detail.type else "Any"
                arg_line = f"    {arg_name} ({type_hint}): {desc}"
                if detail.example:
                    example_str = repr(detail.example) 
                    arg_line += f" Example: {example_str}."
               
                # Append the full body example after the last body-related argument
                if arg_name == last_body_arg_name and request_body_example_str:
                    # Remove the simple Example: only if example_str was defined
                    if example_str and f" Example: {example_str}." in arg_line:
                        arg_line = arg_line.replace(f" Example: {example_str}.", "")
                    elif example_str and f" Example: {example_str}." in arg_line: # Check trailing period just in case
                         arg_line = arg_line.replace(f" Example: {example_str}.","")
                    arg_line += request_body_example_str # Append the formatted JSON example
                    
                args_doc_lines.append(arg_line)
            elif arg_name == "request_body" and has_empty_body:
                 args_doc_lines.append(f"    {arg_name} (dict | None): Optional dictionary for arbitrary request body data.")
                 # Also append example here if this is the designated body arg
                 if arg_name == last_body_arg_name and request_body_example_str: # Ensure this 'if' is indented correctly relative to 'elif'
                     args_doc_lines[-1] += request_body_example_str # Ensure this line is indented correctly relative to the 'if'

    if args_doc_lines:
        docstring_parts.append("\n".join(args_doc_lines))

    # Returns - Use the pre-calculated return_type variable
    success_desc = ""
    responses = operation.get("responses", {})
    for code, resp_info in responses.items():
        if code.startswith("2"):
            success_desc = resp_info.get("description", "").strip()
            break
    docstring_parts.append(f"Returns:\n    {return_type}: {success_desc or 'API response data.'}") # Use return_type
    
    # Tags Section
    operation_tags = operation.get("tags", [])
    if operation_tags:
        tags_string = ", ".join(operation_tags)
        docstring_parts.append(f"Tags:\n    {tags_string}")
            
    # Combine and Format docstring
    docstring_content = "\n\n".join(docstring_parts)
    
    def_indent = "    " 
    doc_indent = def_indent + "    " 
    indented_docstring_content = textwrap.indent(docstring_content, doc_indent).strip()
    
    # Wrap in triple quotes
    formatted_docstring = f'\n{doc_indent}"""\n{indented_docstring_content}\n{doc_indent}"""'
    # ----- End Build Docstring -----
    
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

    # Build query parameters dictionary for the request
    if query_params:
        query_params_items = []
        for param in query_params:
            # Use the original identifier for the key, and the cleaned name for the value variable
            query_params_items.append(f"('{param.identifier}', {param.name})")
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

    # Combine signature, docstring, and body
    method_code = signature + formatted_docstring + "\n" + "\n".join(body_lines)
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
