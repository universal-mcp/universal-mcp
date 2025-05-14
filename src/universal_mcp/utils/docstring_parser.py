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

    # Pattern to capture item key and the start of its description
    # Matches "key:" or "key (type):" followed by description
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
            returns = desc
        elif current_section == "tags":
            # Tags section content is treated as a comma-separated list
            tags.clear()  # Clear existing tags in case of multiple tag sections (unlikely but safe)
            tags.extend([tag.strip() for tag in desc.split(",") if tag.strip()])
        # 'other' sections are ignored in the final output

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
        # Allow "Raises Description:" or "Tags content:"
        elif stripped_lower.startswith(("raises ", "errors ", "exceptions ")):
            section_type = "raises"
            # Capture content after header word and potential colon/space
            parts = re.split(r"[:\s]+", line.strip(), maxsplit=1)  # B034: Use keyword maxsplit
            if len(parts) > 1:
                header_content = parts[1].strip()
        elif stripped_lower.startswith(("tags",)):
            section_type = "tags"
            # Capture content after header word and potential colon/space
            parts = re.split(r"[:\s]+", line.strip(), maxsplit=1)  # B034: Use keyword maxsplit
            if len(parts) > 1:
                header_content = parts[1].strip()

        # Identify other known sections, but don't store their content
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

        # --- Summary Handling ---
        if in_summary:
            if not stripped_line or is_new_section_header:
                # Empty line or section header marks the end of the summary
                in_summary = False
                summary = " ".join(summary_lines).strip()
                summary_lines = []  # Clear summary_lines after finalizing summary

                if not stripped_line:
                    # If the line was just empty, continue to the next line
                    # The new_section_header check will happen on the next iteration if it exists
                    continue
                # If it was a header, fall through to section handling below

            else:
                # Still in summary, append line
                summary_lines.append(stripped_line)
                continue  # Process next line

        # --- Section and Item Handling ---

        # Decide if the previous item/section block should be finalized BEFORE processing the current line
        # Finalize if:
        # 1. A new section header is encountered.
        # 2. An empty line is encountered AFTER we've started collecting content for an item or section.
        # 3. In 'args' or 'raises', we encounter a line that looks like a new key: value pair, or a non-indented line.
        # 4. In 'returns', 'tags', or 'other', we encounter a non-indented line after collecting content.
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
        elif current_section in ["args", "raises"] and current_key is not None:
            # Inside args/raises, processing an item (current_key is set)
            pass  # Logic moved to the combined if statement
        elif current_section in ["returns", "tags", "other"] and current_desc_lines:
            # Inside returns/tags/other, collecting description lines
            pass  # Logic moved to the combined if statement

        # If finalizing the previous item/section
        if should_finalize_previous:
            finalize_current_item()
            # Reset state after finalizing the previous item/section block
            # If it was a new section header, reset everything
            # If it was an end-of-item/block signal within a section, reset key and description lines
            # (The condition for resetting key here is complex but matches the original logic)
            if is_new_section_header or (
                current_section in ["args", "raises"]
                and current_key is not None
                and not key_pattern.match(line)
                and (not stripped_line or original_indentation == 0)
            ):
                current_key = None
            current_desc_lines = []  # Always clear description lines

        # --- Process the current line ---

        # If the current line is a section header
        if is_new_section_header:
            current_section = new_section_type_this_line
            if header_content_this_line:
                # Add content immediately following the header on the same line
                current_desc_lines.append(header_content_this_line)
            continue  # Move to the next line, header is processed

        # If the line is empty, and not a section header (handled above), skip it
        if not stripped_line:
            continue

        # If we are inside a section, process the line's content
        if current_section == "args" or current_section == "raises":
            match = key_pattern.match(line)
            if match:
                # Found a new key: value item within args/raises
                current_key = match.group(1)
                current_desc_lines = [match.group(2).strip()]  # Start new description
            elif current_key is not None:
                # Not a new key, but processing an existing item - append to description
                current_desc_lines.append(stripped_line)
            # Lines that don't match key_pattern and occur when current_key is None
            # within args/raises are effectively ignored by this block, which seems
            # consistent with needing a key: description format.

        elif current_section in ["returns", "tags", "other"]:
            # In these sections, all non-empty, non-header lines are description lines
            current_desc_lines.append(stripped_line)

    # --- Finalization after loop ---
    # Finalize any pending item/section block that was being collected
    finalize_current_item()

    # If the docstring only had a summary (no empty line or section header)
    # ensure the summary is captured. This check is technically redundant
    # because summary is finalized upon hitting the first empty line or header,
    # or falls through to the final finalize call if neither occurs.
    # Keeping it for clarity, though the logic flow should cover it.
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
