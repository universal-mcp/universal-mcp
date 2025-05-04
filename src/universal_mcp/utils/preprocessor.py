import json
import logging
import os
import re
import sys
import time
import traceback

import litellm
import yaml

COLORS = {
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'ENDC': '\033[0m',
    'BLUE': '\033[94m',
    'GREEN': '\033[92m',
}

MAX_DESCRIPTION_LENGTH = 200

class ColoredFormatter(logging.Formatter):
    FORMAT = "%(levelname)s:%(message)s"

    LOG_LEVEL_COLORS = {
        logging.INFO: COLORS['GREEN'],
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

def set_logging_level(level: str):
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    log_level = level_map.get(level.upper(), logging.INFO)
    logger.setLevel(log_level)
    logger.info(f"Logging level set to {logging.getLevelName(log_level)}")

def read_schema_file(schema_path: str) -> dict:
    logger.info(f"Attempting to read schema file: {schema_path}")
    if not os.path.exists(schema_path):
        logger.error(f"Schema file not found at: {schema_path}")
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    try:
        with open(schema_path, encoding='utf-8') as f:
            _, file_extension = os.path.splitext(schema_path)
            file_extension = file_extension.lower()

            if file_extension in ['.yaml', '.yml']:
                logger.info(f"Reading as YAML: {schema_path}")
                return yaml.safe_load(f)
            elif file_extension == '.json':
                logger.info(f"Reading as JSON: {schema_path}")
                return json.load(f)
            else:
                logger.warning(f"Unknown file extension '{file_extension}' for {schema_path}. Attempting to read as YAML.")
                return yaml.safe_load(f)

    except (yaml.YAMLError, json.JSONDecodeError) as e:
        logger.error(f"Error parsing schema file {schema_path}: {e}")
        raise
    except OSError as e:
        logger.error(f"Error reading schema file {schema_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading {schema_path}: {e}")
        traceback.print_exc(file=sys.stderr)
        raise


def write_schema_file(schema_data: dict, output_path: str):
    logger.info(f"Attempting to write processed schema to: {output_path}")
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")

        with open(output_path, 'w', encoding='utf-8') as f:
            _, file_extension = os.path.splitext(output_path)
            file_extension = file_extension.lower()

            if file_extension == '.json':
                json.dump(schema_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Successfully wrote processed schema as JSON to {output_path}")
            elif file_extension in ['.yaml', '.yml']:
                yaml.dump(schema_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                logger.info(f"Successfully wrote processed schema as YAML to {output_path}")
            else:
                logger.error(f"Unsupported output file extension '{file_extension}' for writing.")
                raise ValueError(f"Unsupported output file extension '{file_extension}'. Use .json or .yaml/.yml.")

    except OSError as e:
        logger.error(f"Error writing schema file {output_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while writing {output_path}: {e}")
        traceback.print_exc(file=sys.stderr)
        raise


def generate_description_llm(
    description_type: str,
    model: str,
    context: dict = None,
    max_retries: int = 3,
    retry_delay: int = 5
) -> str:
    if context is None:
        context = {}

    system_prompt = """You are a helpful AI assistant specialized in writing concise summaries for API operations, clear, brief descriptions for API parameters, and overview descriptions for the entire API.
    Respond ONLY with the generated text, without any conversational filler or formatting like bullet points unless the description itself requires it. Ensure the response is a single string suitable for a description field."""

    user_prompt = ""
    fallback_text = "[LLM could not generate description]" # Generic fallback

    if description_type == 'summary':
        path_key = context.get('path_key', 'unknown path')
        method = context.get('method', 'unknown method')
        operation_context_str = json.dumps(context.get('operation_value', {}), indent=None, separators=(',', ':'), sort_keys=True)
        if len(operation_context_str) > 1500:
             operation_context_str = operation_context_str[:1500] + "..."

        user_prompt = f"""Generate a concise one-sentence summary for the API, decsribing what the API does. defined at path "{path_key}" using the "{method.upper()}" method. 
        Example:
         - Stars a GitHub repository using the GitHub API and returns a status message.
         - Retrieves and formats a list of recent commits from a GitHub repository

        Context (operation details): {operation_context_str}
        Respond ONLY with the summary text."""
        fallback_text = f"[LLM could not generate summary for {method.upper()} {path_key}]" # Specific fallback

    elif description_type == 'parameter':
        path_key = context.get('path_key', 'unknown path')
        method = context.get('method', 'unknown method')
        param_name = context.get('param_name', 'unknown parameter')
        param_in = context.get('param_in', 'unknown location')
        param_context_str = json.dumps(context.get('parameter_details', {}), indent=None, separators=(',', ':'), sort_keys=True)
        if len(param_context_str) > 1000:
             param_context_str = param_context_str[:1000] + "..."


        user_prompt = f"""Generate a clear, brief description for the API parameter named "{param_name}" located "{param_in}" for the "{method.upper()}" operation at path "{path_key}".
        Context (parameter details): {param_context_str}
        Respond ONLY with the *SINGLE LINE* description text."""
        fallback_text = f"[LLM could not generate description for parameter {param_name} in {method.upper()} {path_key}]" # Specific fallback

    elif description_type == 'api_description':
        api_title = context.get('title', 'Untitled API')
        user_prompt = f"""Generate a brief overview description for an API titled "{api_title}" based on an OpenAPI schema.
        Respond ONLY with the description text."""
        fallback_text = f"[LLM could not generate description for API '{api_title}']" # Specific fallback

    else:
        logger.error(f"Invalid description_type '{description_type}' passed to generate_description_llm.")
        return "[Invalid description type specified]"

    if not user_prompt:
         logger.error(f"User prompt was not generated for description_type '{description_type}'.")
         return fallback_text


    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    print(f"\n{COLORS['BLUE']}--- LLM Input Prompt ({description_type}) ---{COLORS['ENDC']}")
    print(f"System: {system_prompt}")
    print(f"User: {user_prompt}")
    print(f"{COLORS['BLUE']}------------------------------------------{COLORS['ENDC']}\n")

    for attempt in range(max_retries):
        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                timeout=60
            )

            print(f"\n{COLORS['YELLOW']}--- LLM Raw Response ({description_type}, Attempt {attempt+1}) ---{COLORS['ENDC']}")
            try:
                response_dict = response.model_dump()
            except AttributeError:
                response_dict = response.dict()
            print(json.dumps(response_dict, indent=2))
            print(f"{COLORS['YELLOW']}--------------------------------------------{COLORS['ENDC']}\n")

            if response and response.choices and response.choices[0] and response.choices[0].message:
                 response_text = response.choices[0].message.content.strip()

                 if response_text.startswith('"') and response_text.endswith('"'):
                      response_text = response_text[1:-1].strip()
                 if response_text.startswith("'") and response_text.endswith("'"):
                      response_text = response_text[1:-1].strip()

                 response_text = response_text.strip()

                 if response_text == fallback_text:
                     logger.warning(f"LLM returned the fallback text literally for type '{description_type}'. Treating as failure.")
                     if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                     continue

                 return f"{response_text}"
            else:
                 logger.warning(f"LLM response was empty or unexpected structure for type '{description_type}'. Attempt {attempt+1}/{max_retries}.")
                 if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                 continue

        except Exception as e:
            logger.error(f"Error generating description using LLM for type '{description_type}' (Attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Max retries ({max_retries}) reached for type '{description_type}'.")
                return fallback_text

    return fallback_text


def simplify_operation_context(operation_value: dict) -> dict:
    simplified_context = {}

    original_params = operation_value.get('parameters')
    if isinstance(original_params, list):
        simplified_params_list = []
        for param in original_params:
            if isinstance(param, dict):
                if '$ref' in param:
                     simplified_params_list.append({'$ref': param['$ref']})
                else:
                    simplified_param = {}
                    if 'name' in param:
                        simplified_param['name'] = param['name']
                    if 'in' in param:
                        simplified_param['in'] = param['in']
                    if simplified_param:
                        simplified_params_list.append(simplified_param)
        if simplified_params_list:
            simplified_context['parameters'] = simplified_params_list

    original_responses = operation_value.get('responses')
    if isinstance(original_responses, dict):
         response_status_codes = list(original_responses.keys())
         if response_status_codes:
             simplified_responses_dict = {code: {} for code in response_status_codes}
             simplified_context['responses'] = simplified_responses_dict

    return simplified_context


def simplify_parameter_context(parameter: dict) -> dict:
     simplified_context = {}
     if 'name' in parameter:
         simplified_context['name'] = parameter['name']
     if 'in' in parameter:
         simplified_context['in'] = parameter['in']

     return simplified_context


def process_parameter(
    parameter: dict,
    operation_location_base: str,
    path_key: str,
    method: str,
    llm_model: str
):
    if not isinstance(parameter, dict):
        logger.error(f"Invalid parameter object found in {operation_location_base}. Expected dictionary.")
        return

    if '$ref' in parameter:
        ref_path = parameter['$ref']
        logger.info(f"Parameter in {operation_location_base} is a reference ('{ref_path}'). Skipping description generation.")
        return

    param_name = parameter.get('name')
    param_in = parameter.get('in')

    param_location_id = "unknown_param"
    if isinstance(param_name, str) and param_name.strip():
        param_location_id = param_name.strip()
        if isinstance(param_in, str) and param_in.strip():
            param_location_id = f"{param_in.strip()}:{param_name.strip()}"
    elif isinstance(param_in, str) and param_in.strip():
        param_location_id = f"{param_in.strip()}:[name missing]"


    parameter_location_base = f'{operation_location_base}.parameters[{param_location_id}]'

    is_valid_param = True
    if not isinstance(param_name, str) or not param_name.strip():
        logger.error(f"Missing or empty 'name' field for parameter at {parameter_location_base}. Cannot generate description without name.")
        is_valid_param = False

    if not isinstance(param_in, str) or not param_in.strip():
        logger.error(f"Missing or empty 'in' field for parameter '{param_name}' at {parameter_location_base}. Cannot generate description without location ('in').")
        is_valid_param = False

    if not is_valid_param:
        return

    param_description = parameter.get('description')

    if not isinstance(param_description, str) or not param_description.strip() or param_description.startswith('[LLM could not generate'):
        logger.warning(f"Missing or empty 'description' for parameter '{param_name}' at {parameter_location_base}. Attempting to generate.")

        simplified_context = simplify_parameter_context(parameter)

        generated_description = generate_description_llm(
            description_type='parameter',
            model=llm_model,
            context={
                'path_key': path_key,
                'method': method,
                'param_name': param_name,
                'param_in': param_in,
                'parameter_details': simplified_context
            }
        )
        parameter['description'] = generated_description
        logger.info(f"Generated and inserted description for parameter '{param_name}' at {parameter_location_base}.")
    else:
        logger.info(f"Existing 'description' found for parameter '{param_name}' at {parameter_location_base}.")
  
    # --- Remove URLs from the parameter description --- 
    current_description = parameter.get('description', '')
    if isinstance(current_description, str) and current_description:
        url_pattern = r'https?://[\S]+' 
        modified_description = re.sub(url_pattern, '', current_description).strip()
        modified_description = re.sub(r'\s{2,}', ' ', modified_description).strip()

        if modified_description != current_description:
            parameter['description'] = modified_description
            logger.info(f"Removed links from description for parameter '{param_name}' at {parameter_location_base}. New description: '{modified_description[:50]}...'")
    # --- End URL removal --- 

    # Validate final description length
    final_param_description = parameter.get('description', '')
    if isinstance(final_param_description, str):
        desc_length = len(final_param_description)
        if desc_length > MAX_DESCRIPTION_LENGTH:
            logger.warning(f"Parameter description at '{parameter_location_base}.description' exceeds max length. Actual length: {desc_length}, Max allowed: {MAX_DESCRIPTION_LENGTH}.")


def process_operation(
    operation_value: dict,
    path_key: str,
    method: str,
    llm_model: str
):
    operation_location_base = f'paths.{path_key}.{method.lower()}'

    if not isinstance(operation_value, dict):
         logger.warning(f"Operation value for '{operation_location_base}' is not a dictionary. Skipping.")
         return

    if method.lower().startswith('x-'):
        logger.info(f"Skipping extension operation '{operation_location_base}'.")
        return

    operation_summary = operation_value.get('summary')
    if isinstance(operation_summary, str) and operation_summary.strip() and not operation_summary.startswith('[LLM could not generate'):
        logger.info(f"Existing summary found for '{operation_location_base}'. Attempting to enhance.")
    else:
        logger.warning(f"Missing, empty, or fallback summary for operation '{operation_location_base}'. Attempting to generate.")

    simplified_context = simplify_operation_context(operation_value)

    generated_summary = generate_description_llm(
        description_type='summary',
        model=llm_model,
        context={
            'path_key': path_key,
            'method': method,
            'operation_value': simplified_context
        }
    )
    operation_value['summary'] = generated_summary
    logger.info(f"Generated/Enhanced and inserted summary for '{operation_location_base}'.")

    parameters = operation_value.get('parameters')
    if isinstance(parameters, list):
        for _i, parameter in enumerate(parameters):
            process_parameter(
                parameter,
                operation_location_base,
                path_key,
                method,
                llm_model
            )
    elif parameters is not None:
        logger.warning(f"'parameters' field for operation '{operation_location_base}' is not a list. Skipping parameter processing.")

    final_summary = operation_value.get('summary', '')
    if isinstance(final_summary, str):
        summary_length = len(final_summary)
        if summary_length > MAX_DESCRIPTION_LENGTH:
            logger.warning(f"Operation summary at '{operation_location_base}.summary' exceeds max length. Actual length: {summary_length}, Max allowed: {MAX_DESCRIPTION_LENGTH}.")

def process_paths(paths: dict, llm_model: str):
    if not isinstance(paths, dict):
        logger.warning("'paths' field is not a dictionary. Skipping path processing.")
        return

    for path_key, path_value in paths.items():
        if path_key.lower().startswith('x-'):
             logger.info(f"Skipping path extension '{path_key}'.")
             continue

        if isinstance(path_value, dict):
            for method, operation_value in path_value.items():
                if method.lower() in ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']:
                    process_operation(
                        operation_value,
                        path_key,
                        method,
                        llm_model
                    )
                elif method.lower().startswith('x-'):
                     logger.info(f"Skipping method extension '{method.lower()}' in path '{path_key}'.")
                     continue
                elif method.lower() == 'parameters':
                    continue
                elif operation_value is not None:
                     logger.warning(f"Unknown method '{method}' found in path '{path_key}'. Skipping.")
            if not path_value:
                 logger.warning(f"Path value for '{path_key}' is null or empty. Skipping.")

        elif path_value is not None:
             logger.warning(f"Path value for '{path_key}' is not a dictionary. Skipping.")

def generate_api_description(info_title: str, llm_model: str) -> str:
    """Generates an API description using the LLM based on the API title."""
    logger.info(f"Attempting to generate description for API titled: '{info_title}'")
    generated_description = generate_description_llm(
        description_type='api_description',
        model=llm_model,
        context={'title': info_title}
    )
    return generated_description

def validate_info_section(schema_data: dict, llm_model: str):
    info = schema_data.get('info')
    info_location = 'info'

    if not isinstance(info, dict):
        logger.critical(f"Required '{info_location}' object is missing or not a dictionary.")
        raise ValueError(f"Required '{info_location}' object is missing or not a dictionary.")

    info_title = info.get('title')
    if not isinstance(info_title, str) or not info_title.strip():
        logger.critical(f"Required field '{info_location}.title' is missing or empty.")
        raise ValueError(f"Required field '{info_location}.title' is missing or empty.")
    logger.info(f"'{info_location}.title' found and valid: '{info_title}'")

    info_description = info.get('description')

    fallback_prefix_for_api = f"[LLM could not generate description for API '{info_title}']"
    if not isinstance(info_description, str) or not info_description.strip() or info_description.startswith('[LLM could not generate') or info_description.startswith(fallback_prefix_for_api):
        logger.warning(f"Missing or empty 'description' for '{info_location}'. Attempting to generate using LLM.")

        generated_description = generate_api_description(info_title, llm_model)

        schema_data[info_location]['description'] = generated_description
        logger.info(f"Generated and inserted description for '{info_location}.description'.")
    else:
        logger.info(f"Existing '{info_location}.description' found and valid.")

    final_description = schema_data[info_location].get('description', '')
    if isinstance(final_description, str):
        desc_length = len(final_description)
        if desc_length > MAX_DESCRIPTION_LENGTH:
            logger.warning(f"API description at '{info_location}.description' exceeds max length. Actual length: {desc_length}, Max allowed: {MAX_DESCRIPTION_LENGTH}.")
        
        
def process_schema_with_llm(schema_data: dict, llm_model: str):
    logger.info("Starting schema processing and validation with LLM generation.")

    validate_info_section(schema_data, llm_model)

    paths = schema_data.get('paths')
    process_paths(paths, llm_model)

    logger.info("Schema processing complete.")


def preprocess(schema_file_path: str, llm_model: str = "perplexity/sonar", output_file_path: str = None):
    logger.info(f"Starting script for schema: {schema_file_path}")
    logger.info(f"Using LLM model: {llm_model}")
    set_logging_level('INFO')

    if not os.path.exists(schema_file_path):
         logger.critical(f"FATAL ERROR: Schema file not found at: {schema_file_path}")
         sys.exit(1)

    try:
        schema_data = read_schema_file(schema_file_path)

        process_schema_with_llm(schema_data, llm_model)

        if output_file_path is None:
            base, ext = os.path.splitext(schema_file_path)
            output_file_path = f"{base}_processed{ext}"
            logger.info(f"No output path specified. Defaulting to: {output_file_path}")
        else:
             logger.info(f"Saving processed schema to: {output_file_path}")

        write_schema_file(schema_data, output_file_path)

        logger.info("\n--- Schema Processing and Saving Complete ---")
        logger.info(f"Modified schema saved to: {output_file_path}")

    except (OSError, FileNotFoundError, yaml.YAMLError, json.JSONDecodeError) as e:
        logger.critical(f"FATAL ERROR: File operation or parsing failed: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.critical(f"FATAL ERROR: Schema Validation Failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred during processing: {e}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    schema_path_to_test = "/home/draken/Desktop/Trello_processed.json"
    llm_model_name = "perplexity/sonar"
    output_schema_path = None

    logger.info("Executing script from __main__ block.")

    try:
        preprocess(schema_path_to_test, llm_model=llm_model_name, output_file_path=output_schema_path)

    except SystemExit as e:
         logger.info(f"Script finished with exit code {e.code}")
    except Exception as e:
         logger.critical(f"Script terminated due to an unhandled error outside main: {e}")
         traceback.print_exc(file=sys.stderr)
         sys.exit(1)