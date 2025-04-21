import re
from typing import Any


def parse_docstring(docstring: str | None) -> dict[str, Any]:
    """
    Parses a standard Python docstring into summary, args, returns, raises, and tags.

    Args:
        docstring: The docstring to parse.

    Returns:
        A dictionary with keys 'summary', 'args', 'returns', 'raises', 'tags'.
        'args' is a dict mapping arg names to descriptions.
        'raises' is a dict mapping exception type names to descriptions.
        'tags' is a list of strings extracted from the 'Tags:' section, comma-separated.
    """
    if not docstring:
        return {"summary": "", "args": {}, "returns": "", "raises": {}, "tags": []}

    lines = docstring.strip().splitlines()
    if not lines:
        return {"summary": "", "args": {}, "returns": "", "raises": {}, "tags": []}

    summary = lines[0].strip()
    args = {}
    returns = ""
    raises = {}
    tags: list[str] = []  # Final list of parsed tags
    current_section = None
    current_key = None
    current_desc_lines = []  # Accumulator for multi-line descriptions/tag content
    key_pattern = re.compile(r"^\s*([\w\.]+)\s*(?:\(.*\))?:\s*(.*)")

    def finalize_current_item():
        """Helper function to finalize the currently parsed item."""
        nonlocal returns, tags  # Allow modification of outer scope variables
        desc = " ".join(current_desc_lines).strip()
        if current_section == "args" and current_key:
            args[current_key] = desc
        elif current_section == "raises" and current_key:
            raises[current_key] = desc
        elif current_section == "returns":
            returns = desc
        # SIM102 applied: Combine nested if
        elif current_section == "tags" and desc:  # Only process if there's content
            tags = [tag.strip() for tag in desc.split(",") if tag.strip()]

    # B007 applied: Rename unused loop variable i to _
    for _, line in enumerate(lines[1:]):
        stripped_line = line.strip()
        original_indentation = len(line) - len(line.lstrip(" "))

        section_line = stripped_line.lower()
        is_new_section_header = False
        new_section_type = None
        header_content = ""

        if section_line in ("args:", "arguments:", "parameters:"):
            new_section_type = "args"
            is_new_section_header = True
        elif section_line in ("returns:", "yields:"):
            new_section_type = "returns"
            is_new_section_header = True
        elif section_line.startswith(("raises ", "raises:", "errors:", "exceptions:")):
            new_section_type = "raises"
            is_new_section_header = True
        elif section_line.startswith(
            ("tags:", "tags")
        ):  # Match "Tags:" or "Tags" potentially followed by content
            new_section_type = "tags"
            is_new_section_header = True
            if ":" in stripped_line:
                header_content = stripped_line.split(":", 1)[1].strip()
        elif section_line.endswith(":") and section_line[:-1] in (
            "attributes",
            "see also",
            "example",
            "examples",
            "notes",
        ):
            new_section_type = "other"
            is_new_section_header = True

        finalize_previous = False
        if is_new_section_header:
            finalize_previous = True
        elif current_section in ["args", "raises"] and current_key:
            if key_pattern.match(line) or (original_indentation == 0 and stripped_line):
                finalize_previous = True
        elif current_section in ["returns", "tags"] and current_desc_lines:
            if original_indentation == 0 and stripped_line:
                finalize_previous = True
        # SIM102 applied: Combine nested if/elif
        elif (
            not stripped_line
            and current_desc_lines
            and current_section in ["args", "raises", "returns", "tags"]
            and (current_section not in ["args", "raises"] or current_key)
        ):
            finalize_previous = True

        if finalize_previous:
            finalize_current_item()
            current_key = None
            current_desc_lines = []
            if not is_new_section_header or new_section_type == "other":
                current_section = None

        if is_new_section_header and new_section_type != "other":
            current_section = new_section_type
            # If Tags header had content, start accumulating it
            if new_section_type == "tags" and header_content:
                current_desc_lines.append(header_content)
            # Don't process the header line itself further
            continue

        if not stripped_line:
            continue

        if current_section == "args" or current_section == "raises":
            match = key_pattern.match(line)
            if match:
                current_key = match.group(1)
                current_desc_lines = [match.group(2).strip()]  # Start new description
            elif (
                current_key and original_indentation > 0
            ):  # Check for indentation for continuation
                current_desc_lines.append(stripped_line)

        elif current_section == "returns":
            if not current_desc_lines or original_indentation > 0:
                current_desc_lines.append(stripped_line)

        elif current_section == "tags":
            if (
                original_indentation > 0 or not current_desc_lines
            ):  # Indented or first line
                current_desc_lines.append(stripped_line)

    finalize_current_item()
    return {
        "summary": summary,
        "args": args,
        "returns": returns,
        "raises": raises,
        "tags": tags,
    }


docstring_example = """
    Starts a crawl job for a given URL using Firecrawl. Returns the job ID immediately.

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
        requests.exceptions.ConnectionError: If connection fails.

    Tags:
        crawl, async_job, start, api,  long_tag_example , another
        , final_tag
"""

if __name__ == "__main__":
    parsed = parse_docstring(docstring_example)
    import json

    print(json.dumps(parsed, indent=4))
