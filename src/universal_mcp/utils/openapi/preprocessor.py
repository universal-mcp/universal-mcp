import json
import logging
import os
import re
import sys
import time
import traceback
from pathlib import Path

import litellm
import typer
import yaml
from rich.console import Console

console = Console()


COLORS = {
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "CYAN": "\033[96m",
}


class ColoredFormatter(logging.Formatter):
    FORMAT = "%(levelname)s:%(message)s"

    LOG_LEVEL_COLORS = {
        logging.DEBUG: COLORS["CYAN"],
        logging.INFO: COLORS["GREEN"],
        logging.WARNING: COLORS["YELLOW"],
        logging.ERROR: COLORS["RED"],
        logging.CRITICAL: COLORS["RED"],
    }

    def format(self, record):
        log_format = self.FORMAT

        color_prefix = self.LOG_LEVEL_COLORS.get(record.levelno)

        if color_prefix:
            log_format = color_prefix + log_format + COLORS["ENDC"]

        # Add filename and line number for debug
        if record.levelno == logging.DEBUG:
            log_format = f"%(filename)s:%(lineno)d - {log_format}"

        formatter = logging.Formatter(log_format)

        return formatter.format(record)


logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)

logger.setLevel(logging.INFO)  # Default level, can be changed by set_logging_level

console_handler = logging.StreamHandler(sys.stdout)
colored_formatter = ColoredFormatter()
console_handler.setFormatter(colored_formatter)
logger.addHandler(console_handler)


def set_logging_level(level: str):
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = level_map.get(level.upper(), logging.INFO)
    logger.setLevel(log_level)
    logger.info(f"Logging level set to {logging.getLevelName(log_level)}")


MAX_DESCRIPTION_LENGTH = 200


def is_fallback_text(text: str | None) -> bool:
    """Checks if the text looks like a generated fallback message."""
    if not isinstance(text, str) or not text.strip():
        return False
    # Check for the specific pattern used for LLM generation failures
    return text.strip().startswith("[LLM could not generate")


def read_schema_file(schema_path: str) -> dict:
    # Keep this function as is
    logger.info(f"Attempting to read schema file: {schema_path}")
    if not os.path.exists(schema_path):
        logger.critical(f"Schema file not found at: {schema_path}")  # Use critical for pre-processing essential step
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    try:
        with open(schema_path, encoding="utf-8") as f:
            _, file_extension = os.path.splitext(schema_path)
            file_extension = file_extension.lower()

            if file_extension in [".yaml", ".yml"]:
                logger.info(f"Reading as YAML: {schema_path}")
                return yaml.safe_load(f)
            elif file_extension == ".json":
                logger.info(f"Reading as JSON: {schema_path}")
                return json.load(f)
            else:
                # Attempt YAML as a fallback for unknown extensions
                logger.warning(
                    f"Unknown file extension '{file_extension}' for {schema_path}. Attempting to read as YAML."
                )
                try:
                    return yaml.safe_load(f)
                except (
                    yaml.YAMLError,
                    json.JSONDecodeError,
                ):  # If YAML fails, try JSON
                    f.seek(0)  # Reset file pointer
                    logger.warning("YAML load failed, attempting JSON.")
                    return json.load(f)

    except (yaml.YAMLError, json.JSONDecodeError) as e:
        logger.critical(f"Error parsing schema file {schema_path}: {e}")
        raise
    except OSError as e:
        logger.critical(f"Error reading schema file {schema_path}: {e}")
        raise
    except Exception as e:
        logger.critical(f"An unexpected error occurred while reading {schema_path}: {e}")
        traceback.print_exc(file=sys.stderr)
        raise


def write_schema_file(schema_data: dict, output_path: str):
    # Keep this function as is
    logger.info(f"Attempting to write processed schema to: {output_path}")
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")

        with open(output_path, "w", encoding="utf-8") as f:
            _, file_extension = os.path.splitext(output_path)
            file_extension = file_extension.lower()

            if file_extension == ".json":
                json.dump(schema_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Successfully wrote processed schema as JSON to {output_path}")
            elif file_extension in [".yaml", ".yml"]:
                yaml.dump(
                    schema_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
                logger.info(f"Successfully wrote processed schema as YAML to {output_path}")
            else:
                logger.error(f"Unsupported output file extension '{file_extension}' for writing.")
                raise ValueError(f"Unsupported output file extension '{file_extension}'. Use .json or .yaml/.yml.")

    except OSError as e:
        logger.critical(f"Error writing schema file {output_path}: {e}")
        raise
    except Exception as e:
        logger.critical(f"An unexpected error occurred while writing {output_path}: {e}")
        traceback.print_exc(file=sys.stderr)
        raise


def generate_description_llm(
    description_type: str,
    model: str,
    context: dict = None,
    max_retries: int = 3,
    retry_delay: int = 5,
) -> str:
    if context is None:
        context = {}

    system_prompt = """You are a helpful AI assistant specialized in writing concise summaries for API operations, clear, brief descriptions for API parameters, and overview descriptions for the entire API.
    Respond ONLY with the generated text, without any conversational filler or formatting like bullet points unless the description itself requires it. Ensure the response is a single string suitable for a description field."""

    user_prompt = ""
    # Make fallback text consistent
    fallback_text = f"[LLM could not generate {description_type}]"

    if description_type == "summary":
        path_key = context.get("path_key", "unknown path")
        method = context.get("method", "unknown method")
        operation_context_str = json.dumps(
            context.get("operation_value", {}),
            indent=None,
            separators=(",", ":"),
            sort_keys=True,
        )
        if len(operation_context_str) > 1500:  # Limit context size
            operation_context_str = operation_context_str[:1500] + "..."

        user_prompt = f"""Generate a concise one-sentence summary for the API operation defined at path "{path_key}" using the "{method.upper()}" method.
        Example:
         - Stars a GitHub repository using the GitHub API and returns a status message.
         - Retrieves and formats a list of recent commits from a GitHub repository

        Context (operation details): {operation_context_str}
        Respond ONLY with the summary text."""
        fallback_text = f"[LLM could not generate summary for {method.upper()} {path_key}]"  # More specific fallback

    elif description_type == "parameter":
        path_key = context.get("path_key", "unknown path")
        method = context.get("method", "unknown method")
        param_name = context.get("param_name", "unknown parameter")
        param_in = context.get("param_in", "unknown location")
        param_context_str = json.dumps(
            context.get("parameter_details", {}),
            indent=None,
            separators=(",", ":"),
            sort_keys=True,
        )
        if len(param_context_str) > 1000:  # Limit context size
            param_context_str = param_context_str[:1000] + "..."

        user_prompt = f"""Generate a clear, brief description for the API parameter named "{param_name}" located "{param_in}" for the "{method.upper()}" operation at path "{path_key}".
        Context (parameter details): {param_context_str}
        Respond ONLY with the *SINGLE LINE* description text."""
        fallback_text = f"[LLM could not generate description for parameter {param_name} in {method.upper()} {path_key}]"  # More specific fallback

    elif description_type == "api_description":
        api_title = context.get("title", "Untitled API")
        user_prompt = f"""Generate a brief overview description for an API titled "{api_title}" based on an OpenAPI schema.
        Respond ONLY with the description text."""
        fallback_text = f"[LLM could not generate description for API '{api_title}']"  # More specific fallback

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

    # Temporarily set debug level for prompt/response logging
    original_level = logger.level
    logger.setLevel(logging.DEBUG)

    # logger.debug(
    #     f"\n{COLORS['BLUE']}--- LLM Input Prompt ({description_type}) ---{COLORS['ENDC']}"
    # )
    # logger.debug(f"System: {system_prompt}")
    # logger.debug(f"User: {user_prompt}")
    # logger.debug(
    #     f"{COLORS['BLUE']}------------------------------------------{COLORS['ENDC']}\n"
    # )

    response_text = fallback_text  # Default in case all retries fail

    for attempt in range(max_retries):
        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=150,  # Keep tokens low for concise output
                timeout=60,
            )

            # logger.debug(
            #     f"\n{COLORS['YELLOW']}--- LLM Raw Response ({description_type}, Attempt {attempt+1}) ---{COLORS['ENDC']}"
            # )
            try:
                # Use model_dump() for Pydantic v2, dict() for v1
                response.model_dump()
            except AttributeError:
                response.dict()
            # logger.debug(json.dumps(response_dict, indent=2))
            # logger.debug(
            #     f"{COLORS['YELLOW']}--------------------------------------------{COLORS['ENDC']}\n"
            # )

            if response and response.choices and response.choices[0] and response.choices[0].message:
                response_text = response.choices[0].message.content.strip()

                # Remove potential quotes around the response
                if response_text.startswith('"') and response_text.endswith('"'):
                    response_text = response_text[1:-1].strip()
                if response_text.startswith("'") and response_text.endswith("'"):
                    response_text = response_text[1:-1].strip()

                response_text = response_text.strip()

                # Check if the LLM returned the fallback text literally
                if response_text == fallback_text:
                    logger.warning(
                        f"LLM returned the fallback text literally for type '{description_type}'. Treating as failure. Attempt {attempt + 1}/{max_retries}."
                    )
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    continue  # Retry

                # Check if the response is empty or too short after stripping
                if not response_text:
                    logger.warning(
                        f"LLM response is empty after stripping for type '{description_type}'. Attempt {attempt + 1}/{max_retries}."
                    )
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    continue  # Retry

                # Successful generation
                # logger.debug(f"Generated response: {response_text}")
                return response_text

            else:
                logger.warning(
                    f"LLM response was empty or unexpected structure for type '{description_type}'. Attempt {attempt + 1}/{max_retries}."
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue  # Retry

        except Exception as e:
            logger.error(
                f"Error generating description using LLM for type '{description_type}' (Attempt {attempt + 1}/{max_retries}): {e}"
            )
            traceback.print_exc(file=sys.stderr)  # Print traceback for debugging
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Max retries ({max_retries}) reached for type '{description_type}'.")
                break  # Exit retry loop

    # Restore original logging level
    logger.setLevel(original_level)
    logger.warning(f"Returning fallback text for type '{description_type}'.")
    return fallback_text  # Return fallback if all retries fail


def simplify_operation_context(operation_value: dict) -> dict:
    # Keep this function as is
    simplified_context = {}

    original_params = operation_value.get("parameters")
    if isinstance(original_params, list):
        simplified_params_list = []
        for param in original_params:
            if isinstance(param, dict):
                if "$ref" in param:
                    simplified_params_list.append({"$ref": param["$ref"]})
                else:
                    simplified_param = {}
                    if "name" in param:
                        simplified_param["name"] = param["name"]
                    if "in" in param:
                        simplified_param["in"] = param["in"]
                    # Optionally add type/required for better context, but keep it small
                    if "schema" in param and isinstance(param["schema"], dict) and "type" in param["schema"]:
                        simplified_param["type"] = param["schema"]["type"]
                    if "required" in param:
                        simplified_param["required"] = param["required"]

                    if simplified_param:
                        simplified_params_list.append(simplified_param)
        if simplified_params_list:
            simplified_context["parameters"] = simplified_params_list

    original_responses = operation_value.get("responses")
    if isinstance(original_responses, dict):
        # Only include keys (status codes) to keep context size down
        response_status_codes = list(original_responses.keys())
        if response_status_codes:
            simplified_responses_dict = {code: {} for code in response_status_codes}
            simplified_context["responses"] = simplified_responses_dict

    # Include requestBody if present (simplified)
    original_request_body = operation_value.get("requestBody")
    if isinstance(original_request_body, dict):
        simplified_request_body = {}
        if "required" in original_request_body:
            simplified_request_body["required"] = original_request_body["required"]
        if "content" in original_request_body and isinstance(original_request_body["content"], dict):
            simplified_request_body["content_types"] = list(original_request_body["content"].keys())
        if simplified_request_body:
            simplified_context["requestBody"] = simplified_request_body

    # Include security if present (simplified)
    original_security = operation_value.get("security")
    if isinstance(original_security, list) and original_security:
        simplified_context["security"] = original_security  # List of security requirement objects (usually small)

    return simplified_context


def simplify_parameter_context(parameter: dict) -> dict:
    # Keep this function as is, adding type/required like in operation context simplification
    simplified_context = {}
    if "name" in parameter:
        simplified_context["name"] = parameter["name"]
    if "in" in parameter:
        simplified_context["in"] = parameter["in"]
    if "required" in parameter:
        simplified_context["required"] = parameter["required"]
    if "schema" in parameter and isinstance(parameter["schema"], dict):
        if "type" in parameter["schema"]:
            simplified_context["type"] = parameter["schema"]["type"]
        # Optionally add enum, default?
        if "enum" in parameter["schema"]:
            simplified_context["enum"] = parameter["schema"]["enum"]
        if "default" in parameter["schema"]:
            simplified_context["default"] = parameter["schema"]["default"]

    return simplified_context


def scan_schema_for_status(schema_data: dict):
    """
    Scans the schema to report the status of descriptions/summaries
    and identify critical issues like missing parameter 'name'/'in'.
    Does NOT modify the schema or call the LLM.
    """
    logger.info("\n--- Scanning Schema for Status ---")

    scan_report = {
        "info_description": {"present": 0, "missing": 0, "fallback": 0},
        "operation_summary": {"present": 0, "missing": 0, "fallback": 0},
        "parameter_description": {"present": 0, "missing": 0, "fallback": 0},
        "parameters_missing_name": [],
        "parameters_missing_in": [],
        "critical_errors": [],  # For essential validation issues like missing info/title
    }

    # --- Check Info Section ---
    info = schema_data.get("info")
    info_location = "info"

    if not isinstance(info, dict):
        error_msg = f"Critical: Required '{info_location}' object is missing or not a dictionary."
        logger.critical(error_msg)
        scan_report["critical_errors"].append(error_msg)
        # Cannot proceed meaningfully without info block
        return scan_report

    info_title = info.get("title")
    if not isinstance(info_title, str) or not info_title.strip():
        error_msg = f"Critical: Required field '{info_location}.title' is missing or empty."
        logger.critical(error_msg)
        scan_report["critical_errors"].append(error_msg)
        # Cannot proceed meaningfully without title
        return scan_report

    info_description = info.get("description")
    if isinstance(info_description, str) and info_description.strip():
        if is_fallback_text(info_description):
            scan_report["info_description"]["fallback"] += 1
        else:
            scan_report["info_description"]["present"] += 1
    else:
        scan_report["info_description"]["missing"] += 1

    # --- Check Paths ---
    paths = schema_data.get("paths")
    if not isinstance(paths, dict):
        if paths is not None:  # Allow None if schema is empty, but warn if it's wrong type
            logger.warning("'paths' field is not a dictionary. Skipping path scanning.")
        else:
            logger.info("'paths' field is missing or null. No operations to scan.")
        return scan_report  # No paths to scan

    for path_key, path_value in paths.items():
        if path_key.lower().startswith("x-"):
            logger.debug(f"Skipping scanning of path extension '{path_key}'.")
            continue

        if not isinstance(path_value, dict):
            logger.warning(f"Path value for '{path_key}' is not a dictionary. Skipping scanning for this path.")
            continue

        for method, operation_value in path_value.items():
            if method.lower() in [
                "get",
                "put",
                "post",
                "delete",
                "options",
                "head",
                "patch",
                "trace",
            ]:
                operation_location_base = f"paths.{path_key}.{method.lower()}"
                if not isinstance(operation_value, dict):
                    logger.warning(f"Operation value for '{operation_location_base}' is not a dictionary. Skipping.")
                    continue

                # Check Operation Summary
                operation_summary = operation_value.get("summary")
                if isinstance(operation_summary, str) and operation_summary.strip():
                    if is_fallback_text(operation_summary):
                        scan_report["operation_summary"]["fallback"] += 1
                    else:
                        scan_report["operation_summary"]["present"] += 1
                else:
                    scan_report["operation_summary"]["missing"] += 1

                # Check Parameters
                parameters = operation_value.get("parameters")
                if isinstance(parameters, list):
                    for i, parameter in enumerate(parameters):
                        if not isinstance(parameter, dict):
                            logger.warning(
                                f"Parameter at index {i} in {operation_location_base}.parameters is not a dictionary. Skipping."
                            )
                            continue

                        if "$ref" in parameter:
                            logger.debug(
                                f"Parameter at index {i} in {operation_location_base}.parameters is a reference. Skipping detailed scan."
                            )
                            continue

                        param_name = parameter.get("name")
                        param_in = parameter.get("in")
                        param_location_id = (
                            param_name if isinstance(param_name, str) and param_name.strip() else f"index {i}"
                        )
                        param_location_base = f"{operation_location_base}.parameters[{param_location_id}]"

                        # Check Parameter 'name' and 'in'
                        if not isinstance(param_name, str) or not param_name.strip():
                            error_msg = f"Missing/empty 'name' field for parameter at {param_location_base}. Cannot generate description."
                            logger.warning(error_msg)  # Use warning as it might be fixable manually
                            scan_report["parameters_missing_name"].append(param_location_base)

                        if not isinstance(param_in, str) or not param_in.strip():
                            error_msg = f"Missing/empty 'in' field for parameter '{param_name}' at {param_location_base}. Cannot generate description."
                            logger.warning(error_msg)  # Use warning
                            scan_report["parameters_missing_in"].append(param_location_base)

                        # Check Parameter Description (only if name/in are present for meaningful description)
                        if (
                            isinstance(param_name, str)
                            and param_name.strip()
                            and isinstance(param_in, str)
                            and param_in.strip()
                        ):
                            param_description = parameter.get("description")
                            if isinstance(param_description, str) and param_description.strip():
                                if is_fallback_text(param_description):
                                    scan_report["parameter_description"]["fallback"] += 1
                                else:
                                    scan_report["parameter_description"]["present"] += 1
                            else:
                                scan_report["parameter_description"]["missing"] += 1
                        else:
                            logger.debug(
                                f"Skipping description scan for parameter at {param_location_base} due to missing name/in."
                            )

                elif parameters is not None:
                    logger.warning(
                        f"'parameters' field for operation '{operation_location_base}' is not a list. Skipping parameter scanning."
                    )

            elif method.lower().startswith("x-"):
                logger.debug(f"Skipping scanning of method extension '{method.lower()}' in path '{path_key}'.")
                continue
            elif method.lower() == "parameters":  # Path level parameters
                logger.debug(f"Skipping scanning of path-level parameters in '{path_key}'.")
                continue
            elif operation_value is not None:
                logger.warning(f"Unknown method '{method}' found in path '{path_key}'. Skipping scanning.")
            elif operation_value is None:
                logger.debug(f"Operation value for method '{method}' in path '{path_key}' is null. Skipping scanning.")

    logger.info("--- Scan Complete ---")
    return scan_report


def report_scan_results(scan_report: dict):
    """Prints a formatted summary of the scan results."""
    console = logging.getLogger().handlers[0].console if hasattr(logging.getLogger().handlers[0], "console") else None
    if console is None:  # Fallback if rich console isn't attached to logger
        from rich.console import Console

        console = Console()

    console.print("\n[bold blue]--- Schema Scan Summary ---[/bold blue]")

    if scan_report.get("critical_errors"):
        console.print("[bold red]CRITICAL ERRORS FOUND:[/bold red]")
        for error in scan_report["critical_errors"]:
            console.print(f"  [red]❌[/red] {error}")
        console.print("[bold red]Critical errors prevent automatic generation. Please fix these manually.[/bold red]")
        return  # Stop here if critical errors exist

    console.print("[bold yellow]Description/Summary Status:[/bold yellow]")
    info_desc = scan_report["info_description"]
    op_summ = scan_report["operation_summary"]
    param_desc = scan_report["parameter_description"]

    console.print("  API Description (info.description):")
    console.print(f"    [green]✅ Present[/green]: {info_desc['present']}")
    console.print(f"    [orange1]❓ Missing[/orange1]: {info_desc['missing']}")
    console.print(f"    [yellow]⚠️ Fallback[/yellow]: {info_desc['fallback']}")

    console.print("  Operation Summaries (paths.*.summary):")
    console.print(f"    [green]✅ Present[/green]: {op_summ['present']}")
    console.print(f"    [orange1]❓ Missing[/orange1]: {op_summ['missing']}")
    console.print(f"    [yellow]⚠️ Fallback[/yellow]: {op_summ['fallback']}")

    console.print("  Parameter Descriptions (paths.*.*.parameters.description):")
    console.print(f"    [green]✅ Present[/green]: {param_desc['present']}")
    console.print(f"    [orange1]❓ Missing[/orange1]: {param_desc['missing']}")
    console.print(f"    [yellow]⚠️ Fallback[/yellow]: {param_desc['fallback']}")

    missing_name = scan_report.get("parameters_missing_name", [])
    missing_in = scan_report.get("parameters_missing_in", [])

    if missing_name or missing_in:
        console.print("\n[bold red]Parameter Issues Preventing LLM Generation:[/bold red]")
        console.print(
            "[yellow]Parameters below cannot have descriptions generated by LLM until 'name' and 'in' fields are fixed manually.[/yellow]"
        )
        if missing_name:
            console.print("  [bold red]Missing 'name' field:[/bold red]")
            for path in missing_name:
                console.print(f"    [red]❌[/red] {path}")
        if missing_in:
            console.print("  [bold red]Missing 'in' field:[/bold red]")
            for path in missing_in:
                console.print(f"    [red]❌[/red] {path}")

    total_missing_or_fallback = (
        info_desc["missing"]
        + info_desc["fallback"]
        + op_summ["missing"]
        + op_summ["fallback"]
        + param_desc["missing"]
        + param_desc["fallback"]
    )

    if total_missing_or_fallback > 0:
        console.print(
            f"\n[bold]Total items missing or needing enhancement:[/bold] [orange1]{total_missing_or_fallback}[/orange1]"
        )
    else:
        console.print("\n[bold green]Scan found no missing or fallback descriptions/summaries.[/bold green]")

    console.print("[bold blue]-------------------------[/bold blue]")


def process_parameter(
    parameter: dict,
    operation_location_base: str,
    path_key: str,
    method: str,
    llm_model: str,
    enhance_all: bool,  # New flag
):
    if not isinstance(parameter, dict):
        logger.warning(f"Invalid parameter object found in {operation_location_base}. Expected dictionary.")
        return

    if "$ref" in parameter:
        ref_path = parameter["$ref"]
        logger.debug(
            f"Parameter in {operation_location_base} is a reference ('{ref_path}'). Skipping description generation."
        )
        return

    param_name = parameter.get("name")
    param_in = parameter.get("in")

    param_location_id = "unknown_param"
    if isinstance(param_name, str) and param_name.strip():
        param_location_id = param_name.strip()
        if isinstance(param_in, str) and param_in.strip():
            param_location_id = f"{param_in.strip()}:{param_name.strip()}"
    elif isinstance(param_in, str) and param_in.strip():
        param_location_id = f"{param_in.strip()}:[name missing]"

    parameter_location_base = f"{operation_location_base}.parameters[{param_location_id}]"

    # Crucial check: Cannot generate description without name/in
    if (
        not isinstance(param_name, str)
        or not param_name.strip()
        or not isinstance(param_in, str)
        or not param_in.strip()
    ):
        logger.warning(
            f"Cannot generate description for parameter at {parameter_location_base} due to missing 'name' or 'in' field."
        )
        return  # Skip generation for this parameter

    param_description = parameter.get("description")

    needs_generation = (
        enhance_all  # Generate if enhancing all
        or not isinstance(param_description, str)  # Generate if missing
        or not param_description.strip()  # Generate if empty
        or is_fallback_text(param_description)  # Generate if it's previous fallback text
    )

    if needs_generation:
        logger.info(f"Generating description for parameter '{param_name}' at {parameter_location_base}.")

        simplified_context = simplify_parameter_context(parameter)

        generated_description = generate_description_llm(
            description_type="parameter",
            model=llm_model,
            context={
                "path_key": path_key,
                "method": method,
                "param_name": param_name,
                "param_in": param_in,
                "parameter_details": simplified_context,
            },
        )
        parameter["description"] = generated_description
        logger.debug(f"Inserted description for parameter '{param_name}' at {parameter_location_base}.")
    else:
        logger.debug(
            f"Existing 'description' found for parameter '{param_name}' at {parameter_location_base}. Skipping generation."
        )

    # --- Remove URLs from the parameter description ---
    current_description = parameter.get("description", "")
    if isinstance(current_description, str) and current_description and not is_fallback_text(current_description):
        url_pattern = r"https?://[\S]+"
        modified_description = re.sub(url_pattern, "", current_description).strip()
        modified_description = re.sub(r"\s{2,}", " ", modified_description).strip()  # Collapse multiple spaces

        if modified_description != current_description:
            parameter["description"] = modified_description
            logger.debug(
                f"Removed links from description for parameter '{param_name}' at {parameter_location_base}. New description: '{modified_description[:50]}...'"
            )
    # --- End URL removal ---

    # Validate final description length (after potential generation/cleaning)
    final_param_description = parameter.get("description", "")
    if isinstance(final_param_description, str):
        desc_length = len(final_param_description)
        if desc_length > MAX_DESCRIPTION_LENGTH:
            logger.warning(
                f"Parameter description at '{parameter_location_base}.description' exceeds max length. Actual length: {desc_length}, Max allowed: {MAX_DESCRIPTION_LENGTH}. Consider manual edit."
            )


def process_operation(
    operation_value: dict,
    path_key: str,
    method: str,
    llm_model: str,
    enhance_all: bool,  # New flag
):
    operation_location_base = f"paths.{path_key}.{method.lower()}"

    if not isinstance(operation_value, dict):
        logger.warning(f"Operation value for '{operation_location_base}' is not a dictionary. Skipping processing.")
        return

    if method.lower().startswith("x-"):
        logger.debug(f"Skipping extension operation '{operation_location_base}'.")
        return

    # --- Process Summary ---
    operation_summary = operation_value.get("summary")

    needs_summary_generation = (
        enhance_all
        or not isinstance(operation_summary, str)
        or not operation_summary.strip()
        or is_fallback_text(operation_summary)
    )

    if needs_summary_generation:
        logger.info(f"Generating summary for operation '{operation_location_base}'.")

        simplified_context = simplify_operation_context(operation_value)

        generated_summary = generate_description_llm(
            description_type="summary",
            model=llm_model,
            context={
                "path_key": path_key,
                "method": method,
                "operation_value": simplified_context,
            },
        )
        operation_value["summary"] = generated_summary
        logger.debug(f"Inserted summary for '{operation_location_base}'.")
    else:
        logger.debug(f"Existing summary found for '{operation_location_base}'. Skipping generation.")

    # Validate final summary length (after potential generation)
    final_summary = operation_value.get("summary", "")
    if isinstance(final_summary, str):
        summary_length = len(final_summary)
        if summary_length > MAX_DESCRIPTION_LENGTH:
            logger.warning(
                f"Operation summary at '{operation_location_base}.summary' exceeds max length ({summary_length} > {MAX_DESCRIPTION_LENGTH}). Consider manual edit."
            )

    # --- Process Parameters ---
    parameters = operation_value.get("parameters")
    if isinstance(parameters, list):
        for _i, parameter in enumerate(parameters):
            process_parameter(
                parameter,
                operation_location_base,
                path_key,
                method,
                llm_model,
                enhance_all,  # Pass enhance_all
            )
    elif parameters is not None:
        logger.warning(
            f"'parameters' field for operation '{operation_location_base}' is not a list. Skipping parameter processing."
        )


def process_paths(paths: dict, llm_model: str, enhance_all: bool):  # New flag
    if not isinstance(paths, dict):
        logger.warning("'paths' field is not a dictionary. Skipping path processing.")
        return

    for path_key, path_value in paths.items():
        if path_key.lower().startswith("x-"):
            logger.debug(f"Skipping processing of path extension '{path_key}'.")
            continue

        if isinstance(path_value, dict):
            for method, operation_value in path_value.items():
                if method.lower() in [
                    "get",
                    "put",
                    "post",
                    "delete",
                    "options",
                    "head",
                    "patch",
                    "trace",
                ]:
                    process_operation(operation_value, path_key, method, llm_model, enhance_all)  # Pass enhance_all
                elif method.lower().startswith("x-"):
                    logger.debug(f"Skipping processing of method extension '{method.lower()}' in path '{path_key}'.")
                    continue
                elif method.lower() == "parameters":
                    logger.debug(f"Skipping processing of path-level parameters in '{path_key}'.")
                    continue
                elif operation_value is not None:
                    logger.warning(f"Unknown method '{method}' found in path '{path_key}'. Skipping processing.")
                elif operation_value is None:
                    logger.debug(
                        f"Operation value for method '{method}' in path '{path_key}' is null. Skipping processing."
                    )

        elif path_value is not None:
            logger.warning(f"Path value for '{path_key}' is not a dictionary. Skipping processing.")


def process_info_section(schema_data: dict, llm_model: str, enhance_all: bool):  # New flag
    info = schema_data.get("info")
    info_location = "info"

    # Basic validation handled by scanner/CLI caller, assume info and title exist here

    info_title = info["title"]  # Already validated to exist by CLI caller

    info_description = info.get("description")

    needs_description_generation = (
        enhance_all
        or not isinstance(info_description, str)
        or not info_description.strip()
        or is_fallback_text(info_description)
    )

    if needs_description_generation:
        logger.info(f"Generating description for '{info_location}'.")

        generated_description = generate_description_llm(
            description_type="api_description",
            model=llm_model,
            context={"title": info_title},
        )

        # Ensure 'info' key exists (should due to validation)
        if "info" not in schema_data or not isinstance(schema_data["info"], dict):
            schema_data["info"] = {}  # Should not happen if scan/validation passed
            logger.warning("Re-created missing 'info' key during generation.")

        schema_data["info"]["description"] = generated_description
        logger.debug(f"Inserted description for '{info_location}.description'.")
    else:
        logger.debug("Existing 'info.description' found. Skipping generation.")

    final_description = schema_data.get("info", {}).get("description", "")
    if isinstance(final_description, str):
        desc_length = len(final_description)
        if desc_length > MAX_DESCRIPTION_LENGTH:
            logger.warning(
                f"API description at '{info_location}.description' exceeds max length ({desc_length} > {MAX_DESCRIPTION_LENGTH}). Consider manual edit."
            )


def preprocess_schema_with_llm(schema_data: dict, llm_model: str, enhance_all: bool):  # New flag
    """
    Processes the schema to add/enhance descriptions/summaries using an LLM.
    Decides whether to generate based on the 'enhance_all' flag and existing content.
    Assumes basic schema structure validation (info, title) has already passed.
    """
    logger.info(f"\n--- Starting LLM Generation (enhance_all={enhance_all}) ---")

    process_info_section(schema_data, llm_model, enhance_all)

    paths = schema_data.get("paths")
    process_paths(paths, llm_model, enhance_all)

    logger.info("--- LLM Generation Complete ---")


def run_preprocessing(
    schema_path: Path,
    output_path: Path | None = None,
    model: str = "perplexity/sonar",
    debug: bool = False,
):
    set_logging_level("DEBUG" if debug else "INFO")
    console.print("[bold blue]--- Starting OpenAPI Schema Preprocessor ---[/bold blue]")

    if schema_path is None:
        path_str = typer.prompt(
            "Please enter the path to the OpenAPI schema file (JSON or YAML)",
            prompt_suffix=": ",
        ).strip()
        if not path_str:
            console.print("[red]Error: Schema path is required.[/red]")
            raise typer.Exit(1)
        schema_path = Path(path_str)

    try:
        schema_data = read_schema_file(str(schema_path))
    except (FileNotFoundError, yaml.YAMLError, json.JSONDecodeError, OSError) as e:
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]An unexpected error occurred while reading schema: {e}[/red]")
        raise typer.Exit(1) from e

    # --- Step 2: Scan and Report Status ---
    try:
        scan_report = scan_schema_for_status(schema_data)
        report_scan_results(scan_report)
    except Exception as e:
        console.print(f"[red]An unexpected error occurred during schema scanning: {e}[/red]")
        raise typer.Exit(1) from e

    # --- Step 3: Check for Critical Errors ---
    if scan_report.get("critical_errors"):
        console.print(
            "[bold red]Cannot proceed with generation due to critical errors. Please fix the schema file manually.[/bold red]"
        )
        raise typer.Exit(1)

    # --- Step 4: Determine Prompt Options based on Scan Results ---
    total_missing_or_fallback = (
        scan_report["info_description"]["missing"]
        + scan_report["info_description"]["fallback"]
        + scan_report["operation_summary"]["missing"]
        + scan_report["operation_summary"]["fallback"]
        + scan_report["parameter_description"]["missing"]
        + scan_report["parameter_description"]["fallback"]
    )

    ungeneratable_params = len(scan_report.get("parameters_missing_name", [])) + len(
        scan_report.get("parameters_missing_in", [])
    )

    prompt_options = []
    valid_choices = []
    default_choice = "3"  # Default is always Quit unless there's something missing

    console.print("\n[bold blue]Choose an action:[/bold blue]")

    if total_missing_or_fallback > 0:
        console.print(
            f"[bold]Scan found {total_missing_or_fallback} items that are missing or using fallback text and can be generated/enhanced.[/bold]"
        )
        if ungeneratable_params > 0:
            console.print(
                f"[yellow]Note: {ungeneratable_params} parameters require manual fixing and cannot be generated by the LLM due to missing name/in.[/yellow]"
            )

        prompt_options = [
            "  [1] Generate [bold]only missing[/bold] descriptions/summaries [green](default)[/green]",
            "  [2] Generate/Enhance [bold]all[/bold] descriptions/summaries",
            "  [3] [bold red]Quit[/bold red] (exit without changes)",
        ]
        valid_choices = ["1", "2", "3"]
        default_choice = "1"  # Default to filling missing

    else:  # total_missing_or_fallback == 0
        if ungeneratable_params > 0:
            console.print(
                f"[bold yellow]Scan found no missing/fallback items suitable for generation, but {ungeneratable_params} parameters have missing 'name' or 'in'.[/bold yellow]"
            )
            console.print(
                "[bold yellow]These parameters require manual fixing and cannot be generated by the LLM.[/bold yellow]"
            )
        else:
            console.print("[bold green]Scan found no missing or fallback descriptions/summaries.[/bold green]")

        console.print("[bold blue]You can choose to enhance all existing descriptions or exit.[/bold blue]")

        prompt_options = [
            "  [2] Generate/Enhance [bold]all[/bold] descriptions/summaries",
            "  [3] [bold red]Quit[/bold red] [green](default)[/green]",
        ]
        valid_choices = ["2", "3"]
        default_choice = "3"  # Default to quitting if nothing missing

    for option_text in prompt_options:
        console.print(option_text)

    while True:
        choice = typer.prompt("Enter choice", default=default_choice, show_default=False, type=str).strip()

        if choice not in valid_choices:
            console.print("[red]Invalid choice. Please select from the options above.[/red]")
            continue  # Ask again

        if choice == "3":
            console.print("[yellow]Exiting without making changes.[/yellow]")
            raise typer.Exit(0)
        elif choice == "1":
            enhance_all = False
            break  # Exit prompt loop
        elif choice == "2":
            enhance_all = True
            break  # Exit prompt loop

    perform_generation = False
    if enhance_all or choice == "1" and total_missing_or_fallback > 0:
        perform_generation = True

    if perform_generation:
        console.print(f"[blue]Starting LLM generation with Enhance All: {enhance_all}[/blue]")
        try:
            preprocess_schema_with_llm(schema_data, model, enhance_all)
            console.print("[green]LLM generation complete.[/green]")
        except Exception as e:
            console.print(f"[red]Error during LLM generation: {e}[/red]")
            # Log traceback for debugging
            import traceback

            traceback.print_exc(file=sys.stderr)
            raise typer.Exit(1) from e
    else:
        console.print(
            "[yellow]No missing or fallback items found, and 'Enhance All' was not selected. Skipping LLM generation step.[/yellow]"
        )

    if output_path is None:
        base, ext = os.path.splitext(schema_path)
        output_path = Path(f"{base}_processed{ext}")
        console.print(f"[blue]No output path specified. Defaulting to: {output_path}[/blue]")
    else:
        console.print(f"[blue]Saving processed schema to: {output_path}[/blue]")

    try:
        write_schema_file(schema_data, str(output_path))
    except (OSError, ValueError) as e:
        # write_schema_file logs critical errors, just exit here
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]An unexpected error occurred while writing the schema: {e}[/red]")
        raise typer.Exit(1) from e

    console.print("\n[bold green]--- Schema Processing and Saving Complete ---[/bold green]")
    console.print(f"Processed schema saved to: [blue]{output_path}[/blue]")
    console.print("[bold blue]Preprocessor finished successfully.[/bold blue]")
