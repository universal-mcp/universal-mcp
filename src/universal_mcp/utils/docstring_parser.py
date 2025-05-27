import re
from typing import Any


def parse_docstring(docstring: str | None) -> dict[str, Any]:
    """
    Parses a Python docstring into structured components: summary, arguments,
    return value, raised exceptions, and custom tags.

    Supports multi-line descriptions for each section. Recognizes common section
    headers like 'Args:', 'Returns:', 'Raises:', 'Tags:', etc. Also attempts
    to parse key-value pairs within 'Args:' and 'Raises:' sections.

    Args:
        docstring: The docstring string to parse, or None.

    Returns:
        A dictionary containing the parsed components:
        - 'summary': The first paragraph of the docstring.
        - 'args': A dictionary mapping argument names to their descriptions.
        - 'returns': The description of the return value.
        - 'raises': A dictionary mapping exception types to their descriptions.
        - 'tags': A list of strings found in the 'Tags:' section.
    """
    if not docstring:
        return {"summary": "", "args": {}, "returns": "", "raises": {}, "tags": []}

    lines = docstring.strip().splitlines()
    if not lines:
        return {"summary": "", "args": {}, "returns": "", "raises": {}, "tags": []}

    summary: str = ""
    summary_lines: list[str] = []
    args: dict[str, str] = {}
    returns: str = ""
    raises: dict[str, str] = {}
    tags: list[str] = []

    current_section: str | None = None
    current_key: str | None = None
    current_desc_lines: list[str] = []

    key_pattern = re.compile(r"^\s*([\w\.]+)\s*(?:\(.*\))?:\s*(.*)")

    def finalize_current_item():
        """Processes the collected current_desc_lines and assigns them."""
        nonlocal returns, tags, args, raises
        desc = " ".join(current_desc_lines).strip()

        if current_section == "args" and current_key:
            if desc:
                args[current_key] = desc
        elif current_section == "raises" and current_key:
            if desc:
                raises[current_key] = desc
        elif current_section == "returns":
            if desc:
                returns = desc
        elif current_section == "tags":
            tags.clear()
            tags.extend([tag.strip() for tag in desc.split(",") if tag.strip()])

    def check_for_section_header(line: str) -> tuple[bool, str | None, str]:
        """Checks if a line is a recognized section header."""
        stripped_lower = line.strip().lower()
        section_type: str | None = None
        header_content = ""

        if stripped_lower in ("args:", "arguments:", "parameters:"):
            section_type = "args"
        elif stripped_lower in ("returns:", "yields:"):
            section_type = "returns"
        elif stripped_lower in ("raises:", "errors:", "exceptions:"):
            section_type = "raises"
        elif stripped_lower in ("tags:",):
            section_type = "tags"
        elif stripped_lower.startswith(("raises ", "errors ", "exceptions ")):
            section_type = "raises"
            parts = re.split(r"[:\s]+", line.strip(), maxsplit=1)
            if len(parts) > 1:
                header_content = parts[1].strip()
        elif stripped_lower.startswith(("tags",)):
            section_type = "tags"
            parts = re.split(r"[:\s]+", line.strip(), maxsplit=1)
            if len(parts) > 1:
                header_content = parts[1].strip()

        elif stripped_lower.endswith(":") and stripped_lower[:-1] in (
            "attributes",
            "see also",
            "example",
            "examples",
            "notes",
            "todo",
            "fixme",
            "warning",
            "warnings",
        ):
            section_type = "other"

        return section_type is not None, section_type, header_content

    in_summary = True

    for line in lines:
        stripped_line = line.strip()
        original_indentation = len(line) - len(line.lstrip(" "))
        is_new_section_header, new_section_type_this_line, header_content_this_line = check_for_section_header(line)
        should_finalize_previous = False

        if in_summary:
            if not stripped_line or is_new_section_header:
                in_summary = False
                summary = " ".join(summary_lines).strip()
                summary_lines = []

                if not stripped_line:
                    continue

            else:
                summary_lines.append(stripped_line)
                continue

        if (
            is_new_section_header
            or (not stripped_line and (current_desc_lines or current_key is not None))
            or (
                current_section in ["args", "raises"]
                and current_key is not None
                and (key_pattern.match(line) or (original_indentation == 0 and stripped_line))
            )
            or (
                current_section in ["returns", "tags", "other"]
                and current_desc_lines
                and original_indentation == 0
                and stripped_line
            )
        ):
            should_finalize_previous = True
        elif (
            current_section in ["args", "raises"]
            and current_key is not None
            or current_section in ["returns", "tags", "other"]
            and current_desc_lines
        ):
            pass

        if should_finalize_previous:
            finalize_current_item()
            if is_new_section_header or (
                current_section in ["args", "raises"]
                and current_key is not None
                and not key_pattern.match(line)
                and (not stripped_line or original_indentation == 0)
            ):
                current_key = None
            current_desc_lines = []

        if is_new_section_header:
            current_section = new_section_type_this_line
            if header_content_this_line:
                current_desc_lines.append(header_content_this_line)
            continue

        if not stripped_line:
            continue

        if current_section == "args" or current_section == "raises":
            match = key_pattern.match(line)
            if match:
                current_key = match.group(1)
                current_desc_lines = [match.group(2).strip()]
            elif current_key is not None:
                current_desc_lines.append(stripped_line)

        elif current_section in ["returns", "tags", "other"]:
            current_desc_lines.append(stripped_line)

    finalize_current_item()

    if in_summary:
        summary = " ".join(summary_lines).strip()

    return {
        "summary": summary,
        "args": args,
        "returns": returns,
        "raises": raises,
        "tags": tags,
    }


docstring_example = """
    Starts a crawl job for a given URL using Firecrawl.
Returns the job ID immediately.

    Args:
        url: The starting URL for the crawl.
                It can be a very long url that spans multiple lines if needed.
        params: Optional dictionary of parameters to customize the crawl.
                See API docs for details.
        idempotency_key: Optional unique key to prevent duplicate jobs.

    Returns:
        A dictionary containing the job initiation response on success,
        or a string containing an error message on failure. This description
        can also span multiple lines.

Raises:
        ValueError: If the URL is invalid.
        ConnectionError: If connection fails.

    Tags:
        crawl, async_job, start, api,  long_tag_example , another
        , final_tag
    """

if __name__ == "__main__":
    import json

    parsed = parse_docstring(docstring_example)
    print(json.dumps(parsed, indent=4))
