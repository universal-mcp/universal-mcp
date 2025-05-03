import yaml
import json
import os
import sys # Import sys to exit on error

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

def extract_descriptions_and_validate(schema_data: dict) -> list:
    """
    Extracts all 'description' (and 'summary' for operations) fields
    from specific parts of an OpenAPI schema and performs validation checks.

    Validation Checks:
    - info.description: Required (raises ValueError if missing/empty).
    - paths.*.*.summary: Recommended (logs Warning if missing/empty).
    - paths.*.*.parameters[].description: Recommended (logs Warning if missing/empty).
    - paths.*.*.parameters[].name: Required for parameter object (logs Serious Warning if missing/empty).
    - paths.*.*.parameters[].in: Required for parameter object (logs Serious Warning if missing/empty).

    Args:
        schema_data: The parsed OpenAPI schema as a dictionary.

    Returns:
        A list of dictionaries, where each dictionary contains:
        - 'location': A string indicating where the description was found.
        - 'description': The text of the description (or summary).

    Raises:
        ValueError: If info.description is missing or empty.
    """
    descriptions_found = []
    validation_issues = False # Flag to indicate if any warnings occurred

    # 1. Validate and Extract info.description
    info = schema_data.get('info')
    info_location = 'info'
    if not isinstance(info, dict):
        raise ValueError(f"ERROR: Required '{info_location}' object is missing or not a dictionary.")

    info_description = info.get('description')
    if not isinstance(info_description, str) or not info_description.strip():
        raise ValueError(f"ERROR: Required field '{info_location}.description' is missing or empty.")

    # If found and valid, add to descriptions
    descriptions_found.append({
        'location': info_location,
        'description': info_description.strip()
    })

    # 2. & 3. Validate and Extract from paths (operations and parameters)
    paths = schema_data.get('paths')
    if isinstance(paths, dict):
        for path_key, path_value in paths.items():
            if isinstance(path_value, dict):
                # Iterate through HTTP methods/operations
                for method, operation_value in path_value.items():
                    # Common HTTP methods (lowercase)
                    if method.lower() in ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']:
                         operation_location_base = f'paths.{path_key}.{method.lower()}'
                         if isinstance(operation_value, dict):
                            # 2a. Validate Operation Summary
                            operation_summary = operation_value.get('summary')
                            if not isinstance(operation_summary, str) or not operation_summary.strip():
                                validation_issues = True
                                print(f"WARNING: Missing or empty 'summary' for operation '{operation_location_base}'")
                            else:
                                # Add summary to descriptions found
                                descriptions_found.append({
                                    'location': operation_location_base + '.summary',
                                    'description': operation_summary.strip()
                                })

                            # 2b. (Optional) Validate Operation Description - User asked for 'description at method level'
                            # Let's validate the 'description' field as well, as it's common and important.
                            # The original code didn't extract this specifically, so we'll just validate it here.
                            operation_description = operation_value.get('description')
                            if isinstance(operation_description, str) and operation_description.strip():
                                # If description exists, add it too. Summaries are brief, descriptions are detailed.
                                descriptions_found.append({
                                    'location': operation_location_base + '.description',
                                    'description': operation_description.strip()
                                })
                            # else: # We could add a warning for missing description here too, but summary is usually the primary check

                            # 3. Validate and Extract parameter details
                            parameters = operation_value.get('parameters')
                            if isinstance(parameters, list):
                                for i, parameter in enumerate(parameters):
                                    parameter_location_base = f'{operation_location_base}.parameters[index_{i}]' # Use index initially
                                    if isinstance(parameter, dict):
                                        param_name = parameter.get('name')
                                        param_in = parameter.get('in')

                                        # Validate parameter 'name'
                                        if not isinstance(param_name, str) or not param_name.strip():
                                            validation_issues = True
                                            print(f"SERIOUS WARNING: Missing or empty 'name' field for parameter at {parameter_location_base}")
                                            # Keep index_i in location if name is missing

                                        # Validate parameter 'in'
                                        if not isinstance(param_in, str) or not param_in.strip():
                                            validation_issues = True
                                            # Use name in message if available, otherwise index
                                            param_identifier = param_name if isinstance(param_name, str) and param_name.strip() else f"index_{i}"
                                            print(f"SERIOUS WARNING: Missing or empty 'in' field for parameter '{param_identifier}' at {operation_location_base}")
                                            # Keep index_i in location if 'in' is missing, use name if available
                                            if isinstance(param_name, str) and param_name.strip():
                                                parameter_location_base = f'{operation_location_base}.parameters[{param_name}]'


                                        # If both name and in are present, update the location base for clarity
                                        if isinstance(param_name, str) and param_name.strip() and isinstance(param_in, str) and param_in.strip():
                                            parameter_location_base = f'{operation_location_base}.parameters[{param_in}:{param_name}]'
                                        elif isinstance(param_name, str) and param_name.strip(): # Only name available
                                            parameter_location_base = f'{operation_location_base}.parameters[unknown_in:{param_name}]'
                                        elif isinstance(param_in, str) and param_in.strip(): # Only in available
                                             parameter_location_base = f'{operation_location_base}.parameters[{param_in}:index_{i}]'
                                        # else: keep index_i base location

                                        # Validate parameter 'description'
                                        param_description = parameter.get('description')
                                        if not isinstance(param_description, str) or not param_description.strip():
                                            validation_issues = True
                                            print(f"WARNING: Missing or empty 'description' for parameter '{param_name or f'index_{i}'}' at {operation_location_base}")
                                        else:
                                             # Add parameter description to descriptions found
                                            descriptions_found.append({
                                                'location': parameter_location_base,
                                                'description': param_description.strip()
                                            })
                                    else:
                                        validation_issues = True
                                        print(f"SERIOUS WARNING: Parameter at index {i} in {operation_location_base} is not a dictionary.")


    # Note: This code does not traverse $ref references or look deeply in 'components'.
    # For a more complete solution covering all possible description locations,
    # a recursive approach with $ref resolution would be needed.

    if validation_issues:
        print("\n--- Schema Validation Summary ---")
        print("Warnings and Serious Warnings were logged above.")
        print("---------------------------------\n")

    return descriptions_found

def main(schema_file_path: str):
    """
    Main function to read the schema, extract descriptions, and print them.
    Includes validation checks.

    Args:
        schema_file_path: The path to the OpenAPI schema file.
    """
    print(f"Processing schema file: {schema_file_path}")
    try:
        schema_data = read_schema_file(schema_file_path)

        # Use the new validation function
        descriptions = extract_descriptions_and_validate(schema_data)

        if descriptions:
            print("\n--- Descriptions Found ---")
            # Sort descriptions by location for better readability (optional)
            descriptions.sort(key=lambda x: x['location'])
            for item in descriptions:
                print(f"Location: {item['location']}")
                print(f"Text: {item['description']}") # Changed key name to 'Text' for clarity
                print("-" * 20) # Separator for clarity
        else:
            print("\nNo descriptions found at specified locations (info, operation summary/description, parameter description).")

    except (FileNotFoundError, IOError, yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"\nFATAL ERROR: Failed to read or parse schema: {e}")
        sys.exit(1) # Exit script on fatal read/parse error
    except ValueError as e:
        print(f"\nFATAL ERROR: Schema Validation Failed - {e}")
        sys.exit(1) # Exit script on validation error (missing info.description)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1) # Exit on any other unexpected error

# Example Usage:
if __name__ == "__main__":

    empty_info_desc_file = "/home/draken/Desktop/Trello.json"
    try:
        main(empty_info_desc_file)
    except SystemExit:
        print("Caught SystemExit as expected.")
