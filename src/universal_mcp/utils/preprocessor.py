import yaml
import json
import os

def read_schema_file(schema_path: str) -> dict:
    """
    Reads an OpenAPI schema file, handling both JSON and YAML formats.

    Args:
        schema_path: The path to the OpenAPI schema file.

    Returns:
        A dictionary representing the parsed schema data.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there's an error reading the file.
        yaml.YAMLError: If there's an error parsing a YAML/YML file.
        json.JSONDecodeError: If there's an error parsing a JSON file.
    """
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            # Check file extension to determine format
            _, file_extension = os.path.splitext(schema_path)
            file_extension = file_extension.lower()

            if file_extension in ['.yaml', '.yml']:
                print(f"Reading as YAML: {schema_path}")
                return yaml.safe_load(f)
            elif file_extension == '.json':
                print(f"Reading as JSON: {schema_path}")
                return json.load(f)
            else:
                # Try YAML load as it's more flexible
                print(f"Unknown extension '{file_extension}', attempting YAML load: {schema_path}")
                return yaml.safe_load(f)

    except (yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"Error parsing schema file {schema_path}: {e}")
        raise
    except IOError as e:
        print(f"Error reading schema file {schema_path}: {e}")
        raise

def extract_descriptions(schema_data: dict) -> list:
    """
    Extracts all 'description' fields from specific parts of an OpenAPI schema.

    Focuses on:
    1. info.description
    2. paths.*.*.description (Operation description)
    3. paths.*.*.parameters[].description (Parameter description)

    Args:
        schema_data: The parsed OpenAPI schema as a dictionary.

    Returns:
        A list of dictionaries, where each dictionary contains:
        - 'location': A string indicating where the description was found.
        - 'description': The text of the description.
    """
    descriptions_found = []

    # 1. Extract info.description
    info = schema_data.get('info')
    if isinstance(info, dict):
        description = info.get('description')
        if description is not None and isinstance(description, str):
            descriptions_found.append({
                'location': 'info',
                'description': description.strip()
            })

    # 2. & 3. Extract descriptions from paths (operations and parameters)
    paths = schema_data.get('paths')
    if isinstance(paths, dict):
        for path_key, path_value in paths.items():
            if isinstance(path_value, dict):
                # Iterate through HTTP methods/operations
                for method, operation_value in path_value.items():
                    # Common HTTP methods (lowercase)
                    if method.lower() in ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']:
                         if isinstance(operation_value, dict):
                            # 2. Extract operation description
                            operation_description = operation_value.get('description')
                            if operation_description is not None and isinstance(operation_description, str):
                                descriptions_found.append({
                                    'location': f'paths.{path_key}.{method.lower()}',
                                    'description': operation_description.strip()
                                })

                            # 3. Extract parameter descriptions
                            parameters = operation_value.get('parameters')
                            if isinstance(parameters, list):
                                for i, parameter in enumerate(parameters):
                                    if isinstance(parameter, dict):
                                        param_description = parameter.get('description')
                                        if param_description is not None and isinstance(param_description, str):
                                             # Use parameter name in location if available, otherwise index
                                            param_name = parameter.get('name', f'index_{i}')
                                            param_in = parameter.get('in', 'unknown') # Add 'in' for clarity
                                            descriptions_found.append({
                                                'location': f'paths.{path_key}.{method.lower()}.parameters[{param_in}:{param_name}]',
                                                'description': param_description.strip()
                                            })

    # Note: This code *doesn't* currently traverse $ref references or look in 'components' section.
    # For a more complete solution covering all possible description locations
    # (e.g., schemas, responses, requestBodies in components),
    # a recursive approach with $ref resolution would be needed, which is more complex.
    # This focuses on the specific locations you requested.

    return descriptions_found

def main(schema_file_path: str):
    """
    Main function to read the schema, extract descriptions, and print them.

    Args:
        schema_file_path: The path to the OpenAPI schema file.
    """
    print(f"Processing schema file: {schema_file_path}")
    try:
        schema_data = read_schema_file(schema_file_path)
        descriptions = extract_descriptions(schema_data)

        if descriptions:
            print("\n--- Descriptions Found ---")
            for item in descriptions:
                print(f"Location: {item['location']}")
                print(f"Description: {item['description']}")
                print("-" * 20) # Separator for clarity
        else:
            print("\nNo descriptions found at specified locations.")

    except (FileNotFoundError, IOError, yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"\nFailed to process schema: {e}")

# Example Usage:
if __name__ == "__main__":
    # Create a dummy file with the sample schema for testing
    sample_schema_content = """
{
  "openapi": "3.0.3",
  "info": {
    "title": "Asana",
    "description": "This is the interface for interacting with the [Asana Platform](https://developers.asana.com). Our API reference is generated from our [OpenAPI spec] (https://raw.githubusercontent.com/Asana/openapi/master/defs/asana_oas.yaml).\\n\\nContact Support:\\n Name: Asana Support",
    "version": "1.0.0",
    "contact": {}
  },
  "servers": [
    {
      "url": "https://app.asana.com/api/1.0"
    }
  ],
  "paths": {
    "/allocations/{allocation_gid}": {
      "get": {
        "tags": [
          "Allocations"
        ],
        "summary": "Get an allocation",
        "description": "Returns the complete allocation record for a single allocation.",
        "operationId": "getAnAllocation",
        "parameters": [
          {
            "name": "opt_fields",
            "in": "query",
            "schema": {
              "type": "string",
              "example": "assignee,assignee.name,created_by,created_by.name,effort,effort.type,effort.value,end_date,parent,parent.name,resource_subtype,start_date"
            },
            "description": "This endpoint returns a compact resource, which excludes some properties by default. To include those optional properties, set this query parameter to a comma-separated list of the properties you wish to include."
          },
          {
            "name": "another_param",
            "in": "header",
            "description": "Description for another header parameter."
          }
        ]
      },
      "post": {
          "summary": "Create an allocation",
          "description": "Creates a new allocation record.",
          "operationId": "createAllocation",
          "parameters": []
      }
    },
    "/users": {
        "get": {
            "summary": "List users",
            "description": "Retrieves a list of users in the system.",
            "operationId": "listUsers"
        }
    }
  }
}
"""
    # Define a temporary file name
    temp_schema_file = "/home/draken/OpenAPI/Asana.json"

    # Write the sample content to the temporary file
    try:
        # Call the main function with the path to the temporary file
        main(temp_schema_file)
        
    except Exception as e:
        print(f"An error occurred: {e}")

    # You can replace the above section with a direct call to main
    # with the actual path to your schema file:
    # actual_schema_path = "/path/to/your/schema.yaml" # Or .json
    # main(actual_schema_path)