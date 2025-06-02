import re
from typing import Any


def parse_docstring(docstring: str | None) -> dict[str, Any]:
    """
    Parses a Python docstring into structured components: summary, arguments,
    return value, raised exceptions, and custom tags.

    Supports multi-line descriptions for each section. Recognizes common section
    headers like 'Args:', 'Returns:', 'Raises:', 'Tags:', etc. Also attempts
    to parse key-value pairs within 'Args:' and 'Raises:' sections, including
    type information for arguments if present in the docstring.

    Args:
        docstring: The docstring string to parse, or None.

    Returns:
        A dictionary containing the parsed components:
        - 'summary': The first paragraph of the docstring.
        - 'args': A dictionary mapping argument names to their details,
                  including 'description' and 'type_str' (if found).
                  Example: {"param_name": {"description": "desc...", "type_str": "str"}}
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
    args: dict[str, dict[str, str | None]] = {}
    returns: str = ""
    raises: dict[str, str] = {}
    tags: list[str] = []

    current_section: str | None = None
    current_key: str | None = None
    current_desc_lines: list[str] = []
    current_arg_type_str: str | None = None

    key_pattern = re.compile(r"^\s*([\w\.]+)\s*(?:\((.*?)\))?:\s*(.*)")

    def finalize_current_item():
        nonlocal returns, tags, args, raises, current_arg_type_str
        desc = " ".join(current_desc_lines).strip()

        if current_section == "args" and current_key:
            if desc or current_arg_type_str:
                args[current_key] = {
                    "description": desc,
                    "type_str": current_arg_type_str,
                }
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
        elif stripped_lower.startswith(("tags",)):  # Match "tags" without colon for header content
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
                and stripped_line  # Ensure it's not an empty unindented line (handled by rule 2)
            )
        ):
            should_finalize_previous = True

        if should_finalize_previous:
            finalize_current_item()
            current_key = None
            current_arg_type_str = None
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
                current_arg_type_str = match.group(2).strip() if match.group(2) else None
                current_desc_lines = [match.group(3).strip()]  # Start new description
            elif current_key is not None:  # Continuation line for an existing key
                current_desc_lines.append(stripped_line)
        elif current_section in ["returns", "tags", "other"]:
            current_desc_lines.append(stripped_line)

    finalize_current_item()  # Finalize any pending item at the end of the docstring
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
Creates a new product in the CRM product library to manage the collection of goods and services offered by the company.

Args:
    associations (array): associations
    properties (object): No description provided. Example: "{'description': 'Onboarding service for data product', 'name': '1 year implementation consultation', 'price': '6000.00', 'hs_sku': '191902', 'hs_cost_of_goods_sold': '600.00', 'hs_recurring_billing_period': 'P24M', 'city': 'Cambridge', 'phone': '(877) 929-0687', 'state': 'Massachusetts', 'domain': 'biglytics.net', 'industry': 'Technology', 'amount': '1500.00', 'dealname': 'Custom data integrations', 'pipeline': 'default', 'closedate': '2019-12-07T16:50:06.678Z', 'dealstage': 'presentationscheduled', 'hubspot_owner_id': '910901', 'email': 'bcooper@biglytics.net', 'company': 'Biglytics', 'website': 'biglytics.net', 'lastname': 'Cooper', 'firstname': 'Bryan', 'subject': 'troubleshoot report', 'hs_pipeline': 'support_pipeline', 'hs_pipeline_stage': 'open', 'hs_ticket_priority': 'HIGH', 'quantity': '2', 'hs_product_id': '191902', 'recurringbillingfrequency': 'monthly'}".

Returns:
    dict[str, Any]: successful operation

Raises:
    HTTPError: Raised when the API request fails (e.g., non-2XX status code).
    JSONDecodeError: Raised if the response body cannot be parsed as JSON.

Tags:
    Basic, Another Tag
    Yet Another Tag
"""

if __name__ == "__main__":
    import json

    parsed = parse_docstring(docstring_example)
    print(json.dumps(parsed, indent=4))
