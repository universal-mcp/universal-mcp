import json
import logging
import os
import sys

import yaml

COLORS = {
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'ENDC': '\033[0m',
}

class ColoredFormatter(logging.Formatter):
    FORMAT = "%(levelname)s:%(message)s"

    LOG_LEVEL_COLORS = {
        logging.WARNING: COLORS['YELLOW'],
        logging.ERROR: COLORS['RED'],
        logging.CRITICAL: COLORS['RED'],
    }

    def format(self, record):
        log_format = self.FORMAT

        color_prefix = self.LOG_LEVEL_COLORS.get(record.levelno)

        if color_prefix:
            log_format = color_prefix + log_format + COLORS['ENDC']

        formatter = logging.Formatter(log_format)

        return formatter.format(record)

logger = logging.getLogger()
if not logger.handlers:
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)

    colored_formatter = ColoredFormatter()

    console_handler.setFormatter(colored_formatter)

    logger.addHandler(console_handler)

def read_schema_file(schema_path: str) -> dict:
    if not os.path.exists(schema_path):
        logger.error(f"Schema file not found at: {schema_path}")
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    try:
        with open(schema_path, encoding='utf-8') as f:
            _, file_extension = os.path.splitext(schema_path)
            file_extension = file_extension.lower()

            if file_extension in ['.yaml', '.yml']:
                print(f"Reading as YAML: {schema_path}")
                return yaml.safe_load(f)
            elif file_extension == '.json':
                print(f"Reading as JSON: {schema_path}")
                return json.load(f)
            else:
                print(f"Unknown extension '{file_extension}', attempting YAML load: {schema_path}")
                return yaml.safe_load(f)

    except (yaml.YAMLError, json.JSONDecodeError) as e:
        logger.error(f"Error parsing schema file {schema_path}: {e}")
        raise
    except OSError as e:
        logger.error(f"Error reading schema file {schema_path}: {e}")
        raise

def extract_descriptions_and_validate(schema_data: dict) -> list:
    descriptions_found = []

    info = schema_data.get('info')
    info_location = 'info'
    if not isinstance(info, dict):
        logger.critical(f"Required '{info_location}' object is missing or not a dictionary.")
        raise ValueError(f"Required '{info_location}' object is missing or not a dictionary.")

    info_description = info.get('description')
    if not isinstance(info_description, str) or not info_description.strip():
        logger.critical(f"Required field '{info_location}.description' is missing or empty.")
        raise ValueError(f"Required field '{info_location}.description' is missing or empty.")

    descriptions_found.append({
        'location': info_location,
        'description': info_description.strip()
    })

    paths = schema_data.get('paths')
    if isinstance(paths, dict):
        for path_key, path_value in paths.items():
            if isinstance(path_value, dict):
                for method, operation_value in path_value.items():
                    if method.lower() in ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']:
                         operation_location_base = f'paths.{path_key}.{method.lower()}'
                         if isinstance(operation_value, dict):
                            operation_summary = operation_value.get('summary')
                            if not isinstance(operation_summary, str) or not operation_summary.strip():
                                logger.warning(f"Missing or empty 'summary' for operation '{operation_location_base}'")
                            else:
                                descriptions_found.append({
                                    'location': operation_location_base + '.summary',
                                    'description': operation_summary.strip()
                                })

                            operation_description = operation_value.get('description')
                            if isinstance(operation_description, str) and operation_description.strip():
                                descriptions_found.append({
                                    'location': operation_location_base + '.description',
                                    'description': operation_description.strip()
                                })

                            parameters = operation_value.get('parameters')
                            if isinstance(parameters, list):
                                for i, parameter in enumerate(parameters):
                                    parameter_location_base = f'{operation_location_base}.parameters[index_{i}]'
                                    if isinstance(parameter, dict):
                                        param_name = parameter.get('name')
                                        param_in = parameter.get('in')

                                        if not isinstance(param_name, str) or not param_name.strip():
                                            logger.error(f"Missing or empty 'name' field for parameter at {parameter_location_base}\nPlease add the 'name' before proceeding" )

                                        if not isinstance(param_in, str) or not param_in.strip():
                                            param_identifier = param_name if isinstance(param_name, str) and param_name.strip() else f"index_{i}"
                                            logger.error(f"Missing or empty 'in' field for parameter '{param_identifier}' at {operation_location_base}")
                                            if isinstance(param_name, str) and param_name.strip():
                                                parameter_location_base = f'{operation_location_base}.parameters[{param_name}]'

                                        if isinstance(param_name, str) and param_name.strip() and isinstance(param_in, str) and param_in.strip():
                                            parameter_location_base = f'{operation_location_base}.parameters[{param_in}:{param_name}]'
                                        elif isinstance(param_name, str) and param_name.strip():
                                            parameter_location_base = f'{operation_location_base}.parameters[unknown_in:{param_name}]'
                                        elif isinstance(param_in, str) and param_in.strip():
                                             parameter_location_base = f'{operation_location_base}.parameters[{param_in}:index_{i}]'

                                        param_description = parameter.get('description')
                                        if not isinstance(param_description, str) or not param_description.strip():
                                            logger.warning(f"Missing or empty 'description' for parameter '{param_name or f'index_{i}'}' at {parameter_location_base}")
                                        else:
                                            descriptions_found.append({
                                                'location': parameter_location_base,
                                                'description': param_description.strip()
                                            })
                                    else:
                                        logger.error(f"Parameter at index {i} in {operation_location_base} is not a dictionary.")

    return descriptions_found

def main(schema_file_path: str):
    print(f"Processing schema file: {schema_file_path}")

    try:
        schema_data = read_schema_file(schema_file_path)

        descriptions = extract_descriptions_and_validate(schema_data)

        if descriptions:
            print("\n--- Descriptions Found ---")
            descriptions.sort(key=lambda x: x['location'])
            for item in descriptions:
                print(f"Location: {item['location']}")
                print(f"Text: {item['description']}")
                print("-" * 20)
        else:
            print("\nNo descriptions found at specified locations (info, operation summary/description, parameter description).")

    except (OSError, FileNotFoundError, yaml.YAMLError, json.JSONDecodeError):
        logger.critical("FATAL ERROR: Failed to read or parse schema.")
        sys.exit(1)
    except ValueError:
        logger.critical("FATAL ERROR: Schema Validation Failed.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    schema_path_to_test = "/home/draken/Desktop/Trello.json"
    try:
        main(schema_path_to_test)
    except SystemExit as e:
         logger.info(f"Script exited with code {e.code}")