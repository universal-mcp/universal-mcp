import importlib
import os
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, SecretStr

from universal_mcp.tools import ToolManager
from universal_mcp.types import ToolFormat


class TestCaseOutput(BaseModel):
    """Single test case for LLM structured output (without app_instance)."""

    tools: list[str]
    tasks: list[str]
    validate_query: str


class MultiTestCaseOutput(BaseModel):
    """Multiple test cases for LLM structured output."""

    test_cases: list[TestCaseOutput]


def generate_test_cases(app_name: str, class_name: str, output_dir: str = "tests"):
    """Generate test cases for a given app and write to specified output directory.

    Args:
        app_name: Name of the app (e.g., "outlook")
        class_name: Name of the app class (e.g., "OutlookApp")
        output_dir: Directory to write the test file (default: "tests")
    """
    # Dynamically import the app class
    try:
        module = importlib.import_module(f"universal_mcp_{app_name}.app")
        app_class = getattr(module, class_name)
        app = app_class(integration=None)  # type: ignore
    except ImportError as e:
        raise ImportError(f"Could not import universal_mcp_{app_name}.app: {e}") from e
    except AttributeError as e:
        raise AttributeError(f"Class {class_name} not found in universal_mcp_{app_name}.app: {e}") from e

    tool_manager = ToolManager()
    tool_manager.register_tools_from_app(app, tags=["important"])
    tool_def = tool_manager.list_tools(format=ToolFormat.OPENAI)

    # Extract tool names for splitting
    tool_names = [tool["function"]["name"] for tool in tool_def]
    total_tools = len(tool_names)

    # Create system and user prompts
    system_prompt = """You are an expert QA Developer experienced in writing comprehensive test cases for API applications.

CORE PRINCIPLES:
- Generate MULTIPLE test cases that each focus on 3-4 tools maximum
- Each test case should have exactly 3 validation queries
- Ensure complete coverage of available tools across all test cases
- Create realistic scenarios that mirror actual user workflows
- Split tools logically into related functional groups

MANDATORY RULES:
1. MULTIPLE TEST CASE STRUCTURE:
   - Generate 3 separate test cases
   - Each test case should have 3-4 tools maximum
   - Each test case should have exactly 3 validation queries
   - Distribute all available tools across the test cases
   - Group related tools together (e.g., create+edit+delete, search+list, etc.)

2. TEST CASE INDEPENDENCE:
   - Each test case MUST be completely independent and self-contained
   - Tasks within a test case can ONLY reference steps within the SAME test case
   - NEVER reference "step 1 from Test Case 1" in Test Case 2 - each test case starts fresh
   - If multiple test cases need user_id, each should get it independently in their first task

3. TEST CASE DISTRIBUTION:
   - If there are 9 tools: split as 3,3,3 or 4,3,2
   - If there are 10 tools: split as 4,3,3 or 3,3,4
   - If there are 8 tools: split as 3,3,2
   - Always ensure all tools are covered across all test cases

4. TASK DEPENDENCY MANAGEMENT:
   - Always maintain tool dependency relationships within each test case
   - Ensure tool prerequisites are met before usage within the same test case
   - Include fallback scenarios for tool failures

5. NO PLACEHOLDER VALUES - CRITICAL:
   - NEVER use hardcoded placeholder values like 'user123', 'message_id_123', 'folder_id_456', etc.
   - ALWAYS reference data from previous API calls within the SAME test case
   - Use phrases like: "using the user_id from step 1 of this test case", "with the message_id returned from the previous step"
   - When IDs or identifiers are needed, specify they should come from actual API responses within the current test case
   - Example: "Using the user_id retrieved in step 1, call..." (where step 1 is in the current test case)

6. DYNAMIC DATA FLOW WITHIN TEST CASES:
   - Structure tasks so data flows from one step to the next WITHIN THE SAME TEST CASE
   - First task should typically fetch initial foundational data (user info, list items, etc.)
   - Subsequent tasks should use results from previous tasks in the SAME test case
   - Clearly specify which field/property from previous responses to use
   - Each test case should be runnable independently

7. CRUD OPERATIONS COVERAGE:
   - Analyze available tools to identify CRUD capabilities
   - CREATE: If create/send/compose tools are available, include operations that create new items
   - READ: If list/get/retrieve tools are available, include operations that fetch and display information
   - UPDATE: If update/edit/modify tools are available, include operations that modify existing items
   - DELETE: If delete/remove tools are available, include operations that remove items
   - Group related CRUD operations in the same test case when possible

8. VALIDATION REQUIREMENTS:
   - Each test case must have exactly 3 validation queries
   - Write detailed validation queries for every test case
   - Include both positive and negative validation scenarios
   - Verify data integrity after each operation
   - Check for proper error handling and edge cases

9. FORMATTING STANDARDS:
   - Use single quotes for nested quotes (e.g., "Send message with subject 'Hello World'")
   - Structure tasks in logical sequential order within each test case
   - Include clear, actionable step descriptions
   - Ensure validation queries are specific and measurable

EXAMPLE DATA FLOW PATTERN (WITHIN SAME TEST CASE):
Test Case 1:
- Step 1: "Get the user id."
- Step 2: "Send an email to example@gmail.com saying subject: Hello and message: Hey Agentr"
- Step 3: "List last 3 email in my inbox."
validate_query = (
    "Based on the conversation history, verify: "
    "1. Was a user Id retrieved? "
    "2. Was the email sent successfully (check for success response)? "
    "3. Were exactly 3 emails listed from the inbox (check if response shows 3 numbered items)? "
    "4. Does the sent email content 'Hey Agentr' appear in any of the listed email previews?"
)


"""

    user_prompt = f"""Generate 3 comprehensive test cases for the application using the available tools.

AVAILABLE TOOLS: {tool_def}
TOTAL TOOLS: {total_tools}

CRITICAL REQUIREMENTS:
1. TOOL DISTRIBUTION:
   - Split the {total_tools} available tools across 3 test cases
   - Each test case should have 3-4 tools maximum
   - Group logically related tools together
   - Ensure every tool is used in exactly one test case

2. TEST CASE INDEPENDENCE - CRITICAL:
   - Each test case MUST be completely self-contained and runnable independently
   - NEVER reference steps from other test cases (e.g., don't say "using user_id from Test Case 1")
   - Each test case should start by getting any foundational data it needs (like user_id)
   - Tasks should only reference steps within the SAME test case (e.g., "using the user_id from step 1" where step 1 is in the current test case)

3. DATA FLOW - NO HARDCODED VALUES:
   - NEVER use placeholder values like 'user123', 'id_456', etc.
   - Always reference data from previous API calls within the same test case
   - Structure tasks so each step uses results from previous steps in the same test case
   - Use phrases like: "using the ID returned from step 1", "with the data retrieved in the previous step"

4. TEST CASE DESIGN:
   - Test Case 1: Focus on initial data retrieval and creation operations (3-4 tools)
     * Should start with getting foundational data (e.g., user info, basic listings)
   - Test Case 2: Focus on data manipulation, updates and management (3-4 tools)
     * Should independently get any needed foundational data in its first step
   - Test Case 3: Focus on advanced operations, search, and cleanup (2-4 tools)
     * Should independently get any needed foundational data in its first step

5. TASK DESIGN WITH DEPENDENCIES:
   - Create realistic workflows based on available tool capabilities
   - Follow logical dependency order within each test case (get data first, then use it)
   - Include error handling scenarios with actual API error codes
   - Structure tasks to build upon previous results within the same test case

6. VALIDATION STRATEGY:
   - Each test case must have exactly 3 validation queries
   - Write specific validation queries that check actual API responses
   - Include success criteria and failure conditions
   - Verify data integrity and consistency
   - Check for proper error messages and status codes



Generate the 3 test cases now following these requirements, ensuring NO hardcoded placeholder values and complete test case independence."""

    # Setup LLM
    azure_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    if not azure_api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")

    llm = AzureChatOpenAI(
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "o4-mini"),
        api_key=SecretStr(azure_api_key),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-03-01-preview"),
    )

    # Get structured output from LLM using system and user prompts
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

    structured_llm = llm.with_structured_output(MultiTestCaseOutput)
    response = structured_llm.invoke(messages)

    write_to_file(response, app_name, class_name, output_dir)  # type: ignore

    return response


def write_to_file(multi_test_case: MultiTestCaseOutput, app_name: str, class_name: str, output_dir: str):
    """Regenerate the entire automation_test.py file with multiple test cases."""

    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    file_content = f'''import pytest

from universal_mcp.utils.testing import (
    AutomationTestCase,
    execute_automation_test,
    create_app_with_integration
)
from universal_mcp_{app_name}.app import {class_name}


@pytest.fixture
def {app_name}_app():
    return create_app_with_integration("{app_name}", {class_name})

'''

    # Generate fixtures and test functions for each test case
    for i, test_case in enumerate(multi_test_case.test_cases, 1):
        # Format tools array with proper indentation
        tools_formatted = "[\n"
        for tool in test_case.tools:
            escaped_tool = tool.replace('"', '\\"')
            tools_formatted += f'            "{escaped_tool}",\n'
        tools_formatted += "        ]"

        # Format tasks array with proper indentation
        tasks_formatted = "[\n"
        for task in test_case.tasks:
            escaped_task = task.replace('"', '\\"')
            tasks_formatted += f'            "{escaped_task}",\n'
        tasks_formatted += "        ]"

        # Use triple quotes for validation query to avoid escaping issues
        validation_query = test_case.validate_query

        file_content += f'''
@pytest.fixture
def {app_name}_test_case_{i}({app_name}_app):
    """Test Case {i}"""
    return AutomationTestCase(
        app="{app_name}",
        app_instance={app_name}_app,
        tools={tools_formatted},
        tasks={tasks_formatted},
        validate_query=(
            """{validation_query}"""
        )
    )

'''

    # Generate test functions
    for i, _ in enumerate(multi_test_case.test_cases, 1):
        file_content += f'''
@pytest.mark.asyncio
async def test_{app_name}_test_case_{i}({app_name}_test_case_{i}):
    """Execute test case {i}"""
    await execute_automation_test({app_name}_test_case_{i})
'''

    file_content += "\n\n "

    # Write the entire file
    output_file = output_path / "automation_test.py"
    with open(output_file, "w") as f:
        f.write(file_content)

    from loguru import logger

    logger.info(f"✅ Generated {output_file} with {len(multi_test_case.test_cases)} test cases for {app_name}")
    for i, test_case in enumerate(multi_test_case.test_cases, 1):
        logger.info(f"   Test Case {i}: {len(test_case.tools)} tools, {len(test_case.tasks)} tasks")
