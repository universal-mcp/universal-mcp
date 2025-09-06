import os
from dataclasses import dataclass

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from loguru import logger
from pydantic import BaseModel, SecretStr

from universal_mcp.agentr import AgentrIntegration
from universal_mcp.agentr.client import AgentrClient
from universal_mcp.applications.application import APIApplication, BaseApplication
from universal_mcp.tools import Tool, ToolManager
from universal_mcp.types import ToolFormat


class ValidateResult(BaseModel):
    success: bool
    reasoning: str


def check_application_instance(app_instance: BaseApplication, app_name: str):
    """
    Performs a series of assertions to validate an application instance and its tools.

    This function checks for the following:
    - The application instance is not None.
    - The application instance's name matches the expected application name.
    - The application has at least one tool.
    - Each tool has a non-None name with a valid length (1-47 characters).
    - Each tool has a non-None description.
    - All tool names are unique within the application.
    - The application has at least one tool tagged as "important".

    Args:
        app_instance: The application instance to check. Must be an instance of BaseApplication.
        app_name: The expected name of the application.

    Raises:
        AssertionError: If any of the validation checks fail.
    """

    assert app_instance is not None, f"Application object is None for {app_name}"
    assert app_instance.name == app_name, (
        f"Application instance name '{app_instance.name}' does not match expected name '{app_name}'"
    )

    tools = app_instance.list_tools()
    logger.info(f"Tools for {app_name}: {len(tools)}")
    assert len(tools) > 0, f"No tools found for {app_name}"

    tools = [Tool.from_function(tool) for tool in tools]
    seen_names = set()
    important_tools = []

    for tool in tools:
        assert tool.name is not None, f"Tool name is None for a tool in {app_name}"
        assert 0 < len(tool.name) <= 48, (
            f"Tool name '{tool.name}' for {app_name} has invalid length (must be between 1 and 47 characters)"
        )
        assert tool.description is not None, f"Tool description is None for tool '{tool.name}' in {app_name}"
        # assert 0 < len(tool.description) <= 255, f"Tool description for '{tool.name}' in {app_name} has invalid length (must be between 1 and 255 characters)"
        assert tool.name not in seen_names, f"Duplicate tool name: '{tool.name}' found for {app_name}"
        seen_names.add(tool.name)
        if "important" in tool.tags:
            important_tools.append(tool.name)
    assert len(important_tools) > 0, f"No important tools found for {app_name}"


@dataclass
class AutomationTestCase:
    """Generic test case for automation testing."""

    app: str
    app_instance: APIApplication | None = None
    tools: list[str] | None = None
    tasks: list[str] | None = None
    validate_query: str | None = None


def create_agentr_client(app_name: str) -> AgentrClient:
    """
    Create an AgentrClient with appropriate API key and base URL.

    Args:
        app_name: Name of the application (used for app-specific environment variables)

    Returns:
        AgentrClient instance
    """
    api_key = os.environ.get(f"{app_name.upper()}_API_KEY") or os.environ.get("AGENTR_API_KEY")
    base_url = os.environ.get(f"{app_name.upper()}_BASE_URL") or os.environ.get(
        "AGENTR_BASE_URL", "https://api.agentr.dev"
    )
    return AgentrClient(api_key=api_key, base_url=base_url)


def create_integration(app_name: str) -> AgentrIntegration:
    """
    Create an AgentRIntegration instance with appropriate client.

    Args:
        app_name: Name of the application

    Returns:
        AgentRIntegration instance
    """
    client = create_agentr_client(app_name)
    return AgentrIntegration(name=app_name, client=client)


def create_app_with_integration(app_name: str, app_class: type[APIApplication]) -> APIApplication:
    """
    Create an application instance with integration.

    Args:
        app_name: Name of the application
        app_class: Class of the application to instantiate

    Returns:
        Application instance with integration
    """
    integration = create_integration(app_name)
    return app_class(integration=integration)


def load_app_with_integration(app_name: str, app_class: type[APIApplication]) -> APIApplication:
    """
    Load application instance with real integration.

    Args:
        app_name: Name of the application
        app_class: Class of the application to instantiate

    Returns:
        Instantiated application with integration
    """
    integration = create_integration(app_name)
    return app_class(integration=integration)


async def execute_automation_test(test_case: AutomationTestCase, app_instance: APIApplication | None = None) -> None:
    """
    Execute an automation test case using LangGraph ReAct agent.

    Args:
        test_case: Test case to execute
        app_instance: The application instance to test (optional if provided in test_case)
    """
    tool_manager = ToolManager()

    if app_instance is None:
        app_instance = test_case.app_instance
        if app_instance is None:
            raise ValueError("No app_instance provided in test_case or as parameter")

    all_tools = app_instance.list_tools()
    logger.info(f"Available tools from app: {[getattr(t, '__name__', str(t)) for t in all_tools]}")

    tool_manager.register_tools_from_app(app_instance)

    all_registered = tool_manager.get_tools_by_app(app_name=app_instance.name)
    logger.info(f"All registered tools: {[t.name for t in all_registered]}")

    if test_case.tools:
        tools = tool_manager.list_tools(
            format=ToolFormat.LANGCHAIN, app_name=app_instance.name, tool_names=test_case.tools
        )
    else:
        tools = tool_manager.list_tools(format=ToolFormat.LANGCHAIN, app_name=app_instance.name)

    logger.info(f"Tools for test: {[tool.name for tool in tools]}")

    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "o4-mini")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")

    if not azure_endpoint or not azure_api_key:
        raise ValueError(
            "Azure OpenAI credentials not found. Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables."
        )

    from langchain_openai import AzureChatOpenAI

    llm = AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        azure_deployment=azure_deployment,
        api_key=SecretStr(azure_api_key) if azure_api_key else None,
        api_version=api_version,
    )
    logger.info(f"Using Azure OpenAI with deployment: {azure_deployment}")

    agent = create_react_agent(
        model=llm,
        tools=tools,
    )

    messages = []
    for task in test_case.tasks or []:
        try:
            messages.append(HumanMessage(content=task))
            response = await agent.ainvoke({"messages": messages})
            messages.append(AIMessage(content=response["messages"][-1].content))
            logger.info(f"Task: {task}")
            logger.info(f"Response: {response['messages'][-1].content}")
            logger.info("---")
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback

            traceback.print_exc()
            raise AssertionError(f"Task execution failed: {e}") from e

    if test_case.validate_query:
        messages.append(HumanMessage(content=test_case.validate_query))
        structured_llm = llm.with_structured_output(ValidateResult)
        result = await structured_llm.ainvoke(messages)
        logger.info(f"Validation result: {result}")
        assert result.success, f"Validation failed: {result.reasoning}"
