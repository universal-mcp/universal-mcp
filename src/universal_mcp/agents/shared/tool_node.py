# tool_node.py

import asyncio
from typing import Annotated, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from loguru import logger
from pydantic import BaseModel, Field

from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import AgentrConnection, AgentrToolConfig

# --- LangGraph Agent ---


class AgentState(TypedDict):
    task: str
    apps_required: bool
    relevant_apps: list[str]
    apps_with_tools: AgentrToolConfig
    messages: Annotated[list[AnyMessage], add_messages]
    reasoning: str


class ToolSelectionOutput(BaseModel):
    tool_ids: list[str] = Field(description="The ids of the tools to use")


def build_tool_node_graph(llm: BaseChatModel, registry: ToolRegistry) -> StateGraph:
    """Builds the LangGraph workflow."""

    async def _check_if_app_needed(state: AgentState) -> AgentState:
        """Checks if an external application is needed for the given task."""
        task = state["task"]
        prompt = f"""
            Given the user's task: "{task}"
            Does this task require an external application to be completed?
            Your answer should be a simple "Yes" or "No", followed by a brief explanation.
            For example:
            Yes, an external application is needed to send emails.
            No, this is a general question that can be answered directly.
            """
        response = await llm.ainvoke(prompt)
        content = response.content.strip()
        reasoning = f"Initial check for app requirement. LLM response: {content}"

        if content.lower().startswith("yes"):
            return {
                **state,
                "messages": [AIMessage(content=content)],
                "apps_required": True,
                "reasoning": reasoning,
            }
        else:
            return {
                **state,
                "messages": [AIMessage(content=content)],
                "apps_required": False,
                "reasoning": reasoning,
            }

    async def _find_relevant_apps(state: AgentState) -> AgentState:
        """Identifies relevant apps for the given task, preferring connected apps."""
        task = state["task"]
        all_apps = await registry.list_all_apps()
        connected_apps = await registry.list_connected_apps()
        prompt = """
You are an expert at identifying which applications are needed to complete specific tasks.

TASK: "{task}"

AVAILABLE APPS:
{all_apps}

CONNECTED APPS (user has already authenticated these):
{connected_apps}

INSTRUCTIONS:
1. Analyze the task carefully to understand what functionality is required.
2. Review the available apps and their descriptions to identify which ones could help.
3. If multiple apps can perform the task, prefer connected apps, but you MUST include all relevant apps.
4. Consider apps that provide complementary functionality for complex tasks.
5. Only suggest apps that are directly relevant to the core task requirements.
6. Your output should be a list of app IDs.

"""

        class AppList(BaseModel):
            app_list: list[str]
            reasoning: str

        response = await llm.with_structured_output(AppList).ainvoke(
            input=prompt.format(task=task, all_apps=all_apps, connected_apps=connected_apps)
        )
        app_list = response.app_list
        reasoning = f"Found relevant apps: {app_list}. Reasoning: {response.reasoning}"
        logger.info(f"Found relevant apps: {app_list}.")

        return {
            **state,
            "messages": [AIMessage(content=f"Identified relevant apps: {', '.join(app_list)}")],
            "relevant_apps": app_list,
            "reasoning": state.get("reasoning", "") + "\n" + reasoning,
        }

    async def _select_tools(task: str, tools: list[dict]) -> list[str]:
        """Selects the most appropriate tools from a list for a given task."""
        tool_candidates = [f"{tool['name']}: {tool['description']}" for tool in tools]

        SELECT_TOOL_PROMPT = f"""You are an AI assistant that helps the user perform tasks using various apps (each app has multiple tools).
You will be provided with a task and a list of tools which might be relevant for this task.

Your goal is to select the most appropriate tool for the given task.
<task>
{task}
</task>

<tool_candidates>
 - {tool_candidates}
</tool_candidates>

Only return tool ids.
"""

        response = await llm.with_structured_output(schema=ToolSelectionOutput).ainvoke(input=SELECT_TOOL_PROMPT)

        selected_tool_ids = response.tool_ids
        return selected_tool_ids

    async def _generate_search_query(task: str) -> str:
        """Generates a concise search query from the user's task."""
        prompt = f"""
You are an expert at summarizing a user's task into a concise search query for finding relevant tools.
The query should capture all the main actions or intents of the task.

For example:
Task: "Send an email to abc@the-read-example.com with the subject 'Hello'"
Query: "send email"

Task: "Create a new contact in my CRM for John Doe"
Query: "create contact"

Task: "Find the latest news about artificial intelligence"
Query: "search news"

Task: "Post a message to the #general channel in Slack and create a new issue in Jira"
Query: "send message, create issue"

Task: "{task}"
"""

        class SearchQuery(BaseModel):
            query: str

        response = await llm.with_structured_output(SearchQuery).ainvoke(input=prompt.format(task=task))
        query = response.query
        logger.info(f"Generated search query '{query}' for task '{task}'")
        return query

    async def _search_tools(state: AgentState) -> AgentState:
        """Searches for and filters tools in the relevant apps."""
        task = state["task"]
        logger.info(f"Searching for tools in relevant apps for task: {task}")
        search_query = await _generate_search_query(task)
        apps_with_tools_dict = {}
        reasoning_steps = []
        for app_name in state["relevant_apps"]:
            logger.info(f"Searching for tools in {app_name} for task: {task} with query '{search_query}'")
            found_tools = await registry.search_tools(query=search_query, app_id=app_name)
            selected_tools = await _select_tools(task, found_tools)
            apps_with_tools_dict[app_name] = selected_tools
            reasoning_steps.append(f"For '{app_name}', selected tool(s): {', '.join(selected_tools)}.")

        agentr_servers = {app_name: AgentrConnection(tools=tools) for app_name, tools in apps_with_tools_dict.items()}
        tool_config = AgentrToolConfig(agentrServers=agentr_servers)

        return {
            **state,
            "apps_with_tools": tool_config,
            "reasoning": state.get("reasoning", "") + "\n" + "\n".join(reasoning_steps),
        }

    def _handle_no_apps_found(state: AgentState) -> AgentState:
        """Handles the case where no relevant apps are found."""
        reasoning = "No suitable application was found among the available apps."
        return {
            **state,
            "apps_with_tools": AgentrToolConfig(agentrServers={}),
            "reasoning": state.get("reasoning", "") + "\n" + reasoning,
        }

    workflow = StateGraph(AgentState)

    workflow.add_node("check_if_app_needed", _check_if_app_needed)
    workflow.add_node("find_relevant_apps", _find_relevant_apps)
    workflow.add_node("search_tools", _search_tools)
    workflow.add_node("handle_no_apps_found", _handle_no_apps_found)

    workflow.set_entry_point("check_if_app_needed")

    workflow.add_conditional_edges(
        "check_if_app_needed",
        lambda state: "find_relevant_apps" if state["apps_required"] else END,
    )
    workflow.add_conditional_edges(
        "find_relevant_apps",
        lambda state: "search_tools" if state["relevant_apps"] else "handle_no_apps_found",
    )

    workflow.add_edge("search_tools", END)
    workflow.add_edge("handle_no_apps_found", END)

    return workflow.compile()


async def main():
    from universal_mcp.agentr.registry import AgentrRegistry
    from universal_mcp.agents.llm import load_chat_model

    registry = AgentrRegistry()
    llm = load_chat_model("gemini/gemini-2.5-flash")
    graph = build_tool_node_graph(llm, registry)
    initial_state = {
        "task": "Send an email to manoj@agentr.dev",
        "messages": [HumanMessage(content="Send an email to manoj@agentr.dev")],
    }
    result = await graph.ainvoke(initial_state)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
