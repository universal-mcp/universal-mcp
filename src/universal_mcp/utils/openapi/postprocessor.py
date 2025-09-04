import ast
import re

import litellm


def add_hint_tags_to_docstrings(input_path: str, output_path: str):
    """
    Reads a Python API client file, inspects each function, and adds appropriate tags to the docstring:
    - 'readOnlyHint': Tool does not modify its environment (fetching, reading, etc.)
    - 'destructiveHint': Tool may perform destructive updates
    - 'openWorldHint': Tool interacts with external entities (3rd party APIs)

    Functions can have multiple tags (e.g., 'readOnlyHint, openWorldHint').
    Does not alter other tags in the docstring.
    Writes the modified code to output_path.
    """
    with open(input_path, encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)

    # Initialize counters
    total_functions = 0
    functions_with_http_methods = 0
    functions_processed_by_llm = 0
    functions_tagged = 0
    llm_failures = 0

    class DocstringTagAdder(ast.NodeTransformer):
        def _find_http_method(self, node):
            """Find the HTTP method used in the function body."""
            http_methods = []

            def visit_node(n):
                if (
                    isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and isinstance(n.func.value, ast.Name)
                    and n.func.value.id == "self"
                    and n.func.attr in ["_get", "_post", "_put", "_patch", "_delete"]
                ):
                    http_methods.append(n.func.attr[1:])
                for child in ast.iter_child_nodes(n):
                    visit_node(child)

            visit_node(node)
            return http_methods[0] if http_methods else None

        def visit_FunctionDef(self, node):
            nonlocal \
                total_functions, \
                functions_with_http_methods, \
                functions_processed_by_llm, \
                functions_tagged, \
                llm_failures

            total_functions += 1
            from loguru import logger

            logger.info(f"Processing function: {node.name} ({total_functions})")

            http_method = self._find_http_method(node)
            tag_to_add = None

            if http_method:
                functions_with_http_methods += 1
                logger.debug(f"Found HTTP method: {http_method.upper()}")

                # Use simple agent to decide tag
                logger.debug("Calling LLM to determine tag...")
                tag_to_add = self._get_tag_suggestion_from_agent(node, http_method)

                if tag_to_add:
                    functions_processed_by_llm += 1
                    logger.info(f"LLM suggested tags: {tag_to_add}")
                else:
                    logger.warning("LLM failed or returned invalid response")
            else:
                logger.debug("No HTTP method found - skipping")

            if tag_to_add:
                docstring = ast.get_docstring(node, clean=False)
                if docstring is not None:
                    # Look for Tags: section in the docstring
                    tags_match = re.search(r"Tags:\s*(.+)", docstring, re.DOTALL)
                    if tags_match:
                        tags_line = tags_match.group(1).strip()
                        # Parse existing tags
                        existing_tags = [tag.strip() for tag in tags_line.split(",")]

                        # Parse new tags to add
                        new_tags_to_add = [tag.strip() for tag in tag_to_add.split(",")]
                        tags_to_add = [tag for tag in new_tags_to_add if tag not in existing_tags]

                        if tags_to_add:
                            # Add the new tags to the existing list
                            new_tags_line = tags_line.rstrip() + f", {', '.join(tags_to_add)}"
                            new_docstring = re.sub(r"(Tags:\s*)(.+)", r"\1" + new_tags_line, docstring, flags=re.DOTALL)
                            # Replace docstring
                            if isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                                node.body[0].value.value = new_docstring
                                functions_tagged += 1
                                logger.info(f"Tags '{', '.join(tags_to_add)}' added successfully")
                        else:
                            logger.warning(f"All tags '{tag_to_add}' already exist - skipping")
                    else:
                        logger.warning("No 'Tags:' section found in docstring - skipping")
                else:
                    logger.warning("No docstring found - skipping")
            return node

        def _get_tag_suggestion_from_agent(self, node, http_method):
            """Use a simple agent to decide which tag to add based on function context."""

            function_name = node.name
            docstring = ast.get_docstring(node, clean=False) or ""
            parameters = [arg.arg for arg in node.args.args if arg.arg != "self"]

            system_prompt = """You are an expert at analyzing API functions and determining their characteristics.

            Your task is to analyze each function and decide which tags to add:
            - 'readOnlyHint': Tool does not modify its environment (fetching, reading, etc.)
            - 'destructiveHint': Tool may perform destructive updates
            - 'openWorldHint': Tool interacts with external entities (3rd party APIs)

            IMPORTANT:
            - HTTP method alone is NOT enough to determine the tags. You must analyze the function's actual purpose.
            - Since these are all API client functions, MOST functions should have 'openWorldHint' (they interact with external APIs).
            - Only functions that are purely local operations (like reading local files) should NOT have 'openWorldHint'.

            Functions can have multiple tags. For example:
            - A function that reads from Gmail API: 'readOnlyHint, openWorldHint'
            - A function that deletes from GitHub API: 'destructiveHint, openWorldHint'
            - A function that only reads local files: 'readOnlyHint' (no openWorldHint)

            Respond with comma-separated tags (e.g., 'readOnlyHint, openWorldHint') or 'none' if no tags apply."""

            user_prompt = f"""Analyze this API function and decide which tags to add:

Function Name: {function_name}
HTTP Method: {http_method}
Parameters: {", ".join(parameters)}
Docstring: {docstring[:1000]}...

Based on this information, which tags should this function get?

Think through:
1. What does this function actually do? (from name and docstring)
2. Does it modify its environment or just read/fetch?
3. Does it interact with external entities (3rd party APIs)?
4. Could it be potentially destructive?

GUIDELINES for readOnlyHint (does not modify environment):
- Functions that only READ or FETCH data
- Functions that VALIDATE or CHECK things without saving
- Functions that EXPORT or DOWNLOAD data
- Functions that perform HEALTH CHECKS or PING operations
- Functions that REFRESH tokens or sessions
- Functions that SEARCH or FILTER data
- Functions that GET information without changing anything
- Functions that LIST or RETRIEVE data

GUIDELINES for destructiveHint (DESTROYS or DELETES things):
- Functions that DELETE resources or data
- Functions that REMOVE or ERASE things
- Functions that DESTROY or TERMINATE resources
- Functions that CANCEL or ABORT operations
- Functions that REVOKE or INVALIDATE things

IMPORTANT:
- A function should NOT have both readOnlyHint and destructiveHint - they are mutually exclusive.
- Creating, sending, or updating things is NOT destructive - only deleting/destroying is destructive.
- Functions that CREATE, SEND, UPDATE, or MODIFY should NOT get destructiveHint.

GUIDELINES for openWorldHint (interacts with external entities):
- Functions that interact with 3rd party APIs (Gmail, Outlook, Reddit, GitHub, etc.)
- Functions that make external HTTP requests
- Functions that connect to external services
- Functions that interact with cloud services
- Functions that communicate with external databases
- Functions that call external webhooks
- MOST API client functions will have this tag since they interact with external APIs

NOT openWorldHint (local operations):
- Functions that only read local files
- Functions that process local data
- Functions that work with local databases
- Functions that manipulate local variables
- Functions that only work with local system resources

Examples:
- Gmail API read function: 'readOnlyHint, openWorldHint'
- Gmail API send email: 'openWorldHint' (not destructive, just sending)
- Gmail API create draft: 'openWorldHint' (not destructive, just creating)
- GitHub API delete repository: 'destructiveHint, openWorldHint'
- Local file reader: 'readOnlyHint' (no openWorldHint)
- Local data processor: 'none' (no tags)

Focus on the FUNCTION'S PURPOSE, not just the HTTP method.

Your answer (comma-separated tags or 'none'):"""

            try:
                response = litellm.completion(
                    model="perplexity/sonar-pro",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    temperature=0.1,
                    max_tokens=50,
                )

                suggested_tags = response.choices[0].message.content.strip().lower()

                if suggested_tags == "none":
                    return None

                # Parse comma-separated tags
                tag_list = [tag.strip() for tag in suggested_tags.split(",")]
                valid_tags = []

                for tag in tag_list:
                    if tag == "readonlyhint":
                        valid_tags.append("readOnlyHint")
                    elif tag == "destructivehint":
                        valid_tags.append("destructiveHint")
                    elif tag == "openworldhint":
                        valid_tags.append("openWorldHint")

                if valid_tags:
                    return ", ".join(valid_tags)
                else:
                    # If LLM gives unexpected response, return None (no tag added)
                    return None

            except Exception as e:
                nonlocal llm_failures
                llm_failures += 1
                from loguru import logger

                logger.error(f"LLM failed for function {function_name}: {e}")
                # If LLM fails, return None (no tag added)
                return None

    new_tree = DocstringTagAdder().visit(tree)
    ast.fix_missing_locations(new_tree)
    new_source = ast.unparse(new_tree)

    # Print summary statistics
    from loguru import logger

    logger.info("📊 PROCESSING SUMMARY")
    logger.info(f"Total functions processed: {total_functions}")
    logger.info(f"Functions with HTTP methods: {functions_with_http_methods}")
    logger.info(f"Functions processed by LLM: {functions_processed_by_llm}")
    logger.info(f"Functions successfully tagged: {functions_tagged}")
    logger.info(f"LLM failures: {llm_failures}")
    if functions_with_http_methods > 0:
        logger.info(
            f"LLM success rate: {(functions_processed_by_llm / functions_with_http_methods * 100):.1f}% of HTTP functions"
        )

    # Format with Black in memory
    try:
        import black

        formatted_content = black.format_file_contents(new_source, fast=False, mode=black.FileMode())
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_content)
        logger.info(f"Black formatting applied successfully to: {output_path}")
    except ImportError:
        logger.warning(f"Black not installed. Skipping formatting for: {output_path}")
        # Write unformatted version if Black is not available
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_source)
    except Exception as e:
        logger.error(f"Black formatting failed for {output_path}: {e}")
        # Write unformatted version if Black formatting fails
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_source)
