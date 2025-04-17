import re
from typing import Any


def parse_docstring(docstring: str | None) -> dict[str, Any]:
    """
    Parses a standard Python docstring into summary, args, returns, and raises.

    Args:
        docstring: The docstring to parse.

    Returns:
        A dictionary with keys 'summary', 'args', 'returns', 'raises'.
        'args' is a dict mapping arg names to descriptions.
        'raises' is a dict mapping exception type names to descriptions.
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
    tags: list[str] = []
    current_section = None
    current_key = None
    current_desc_lines = []

    # Regex to find args/raises lines: "key (type): description" or "key: description"
    # Allows for optional type hints for args, captures key and description
    key_pattern = re.compile(r"^\s*([\w\.]+)\s*(?:\(.*\))?:\s*(.*)") # \w includes _, . allows for exception paths

    for line in lines[1:]:
        stripped_line = line.strip()

        if not stripped_line: # Skip empty lines between sections
            # If we hit an empty line within the tags section, treat it as the end of that tag section
            # This prevents accidentally merging later content into tags if indentation is missing
            if current_section == "tags":
                current_section = None # Assume end of tags section on empty line
            continue

        # --- Section Detection ---
        section_line = stripped_line.lower()
        is_new_section_header = False
        new_section_type = None

        if section_line in ("args:", "arguments:", "parameters:"):
            new_section_type = "args"
            is_new_section_header = True
        elif section_line in ("returns:", "yields:"):
            new_section_type = "returns"
            is_new_section_header = True
        elif section_line.startswith(("raises ", "raises:", "errors:", "exceptions:")):
            new_section_type = "raises"
            is_new_section_header = True
        elif section_line.startswith(("tags:", "tags")):
            new_section_type = "tags"
            is_new_section_header = True
        elif section_line.startswith(("attributes:", "see also:", "example:", "examples:", "notes:")):
            # Other common sections where we might stop processing previous ones
            new_section_type = "other"
            is_new_section_header = True

        # --- Finalize Previous Item ---
        finalize_previous = False
        if is_new_section_header or current_section in ["args", "raises"] and current_key and not line.startswith(' ') or current_section == "returns" and current_desc_lines and not line.startswith(' '):
            finalize_previous = True
        # Tags are simpler: finalize if we encounter a non-indented line that isn't a section header
        elif current_section == "tags" and tags and not line.startswith(' ') and not is_new_section_header:
            finalize_previous = True # End of tags section if indentation breaks


        if finalize_previous:
            if current_section == "args" and current_key:
                args[current_key] = " ".join(current_desc_lines).strip()
            elif current_section == "raises" and current_key:
                raises[current_key] = " ".join(current_desc_lines).strip()
            elif current_section == "returns":
                returns = " ".join(current_desc_lines).strip()
            # No specific finalization needed for tags list itself here, just reset state

            current_key = None
            current_desc_lines = []
            
            # Update current_section: None if indentation broke, otherwise the new section type
            current_section = None if not is_new_section_header else new_section_type
            
            # If the current line was just a header, skip to the next line
            if is_new_section_header:
                continue

        # --- Process Line Content ---
        if current_section == "args" or current_section == "raises":
            match = key_pattern.match(line) # Match against original line for indentation check
            if match:
                if current_key:
                    desc = " ".join(current_desc_lines).strip()
                    if current_section == "args":
                        args[current_key] = desc
                    elif current_section == "raises":
                        raises[current_key] = desc
                current_key = match.group(1)
                current_desc_lines = [match.group(2).strip()]
            elif current_key and line.startswith(' '): # Check for indentation for continuation
                current_desc_lines.append(stripped_line)
            # else: Line doesn't match key format and isn't indented -> potentially end of section or ignored line

        elif current_section == "returns":
            if not current_desc_lines or line.startswith(' '):
                current_desc_lines.append(stripped_line)
            # else: line doesn't look like continuation -> end of section handled above

        elif current_section == "tags": # <-- Process lines in the Tags section
            # Tags are just lines of text under the header, usually indented
            # Allow non-indented tags if they directly follow the header
            if line.startswith(' ') or not tags: # Check indentation or if it's the first tag
                tags.append(stripped_line)

    if current_key:
        desc = " ".join(current_desc_lines).strip()
        if current_section == "args":
            args[current_key] = desc
        elif current_section == "raises":
            raises[current_key] = desc
    elif current_section == "returns" and not returns:
        returns = " ".join(current_desc_lines).strip()

    # Return the complete dictionary including tags
    return {"summary": summary, "args": args, "returns": returns, "raises": raises, "tags": tags}
