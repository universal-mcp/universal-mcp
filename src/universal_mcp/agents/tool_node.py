# tool_node.py

import asyncio
from typing import Annotated, Any, TypedDict, cast

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from loguru import logger
from pydantic import BaseModel

from universal_mcp.agents.bigtool.prompts import SELECT_TOOL_PROMPT
from universal_mcp.tools.registry import ToolRegistry

# --- LangGraph Agent ---


class AgentState(TypedDict):
    task: str
    apps_required: bool
    apps_with_tools: dict[str, list[str]]
    relevant_apps: list[str]
    messages: Annotated[list[AnyMessage], add_messages]
    reasoning: str


class ToolSelectionOutput(TypedDict):
    tool_names: list[str]


class ToolFinderAgent:
    """
    An agent that suggests applications and tools for a given task.
    """

    def __init__(self, llm: Any, registry: ToolRegistry):
        self.llm = llm
        self.registry = registry
        self.workflow = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Builds the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        workflow.add_node("check_if_app_needed", self._check_if_app_needed)
        workflow.add_node("find_relevant_apps", self._find_relevant_apps)
        workflow.add_node("search_tools", self._search_tools)
        workflow.add_node("handle_no_apps_found", self._handle_no_apps_found)

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

    def _check_if_app_needed(self, state: AgentState) -> AgentState:
        """Checks if an external application is needed for the given task."""
        task = state["task"]
        prompt = PromptTemplate(
            template="""
            Given the user's task: "{task}"
            Does this task require an external application to be completed?
            Your answer should be a simple "Yes" or "No", followed by a brief explanation.
            For example:
            Yes, an external application is needed to send emails.
            No, this is a general question that can be answered directly.
            """,
            input_variables=["task"],
        )
        chain = prompt | self.llm
        response = chain.invoke({"task": task})
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

    async def _find_relevant_apps(self, state: AgentState) -> AgentState:
        """Identifies relevant apps for the given task, preferring connected apps."""
        task = state["task"]
        all_apps = await self.registry.list_all_apps()
        connected_apps = await self.registry.list_connected_apps()
        prompt = PromptTemplate(
            template="""
You are an expert at identifying which applications are needed to complete specific tasks.

TASK: "{task}"

AVAILABLE APPS:
{all_apps}

CONNECTED APPS (user has already authenticated these):
{connected_apps}

INSTRUCTIONS:
1. Analyze the task carefully to understand what functionality is required
2. Review the available apps and their descriptions to identify which ones could help
3. STRONGLY PREFER connected apps when multiple options exist - these are ready to use
4. Consider apps that provide complementary functionality for complex tasks
5. Only suggest apps that are directly relevant to the core task requirements

            """,
            input_variables=["task", "all_apps", "connected_apps"],
        )

        class AppList(BaseModel):
            app_list: list[str]
            reasoning: str

        response = await self.llm.with_structured_output(AppList).ainvoke(
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

    async def _select_tools(self, task: str, tools: list[dict]) -> list[str]:
        """Selects the most appropriate tools from a list for a given task."""
        tool_candidates = [f"{tool['name']}: {tool['description']}" for tool in tools]

        response = await self.llm.with_structured_output(schema=ToolSelectionOutput, method="json_mode").ainvoke(
            SELECT_TOOL_PROMPT.format(tool_candidates="\n - ".join(tool_candidates), task=task)
        )

        selected_tool_names = cast(ToolSelectionOutput, response)["tool_names"]
        return selected_tool_names

    async def _generate_search_query(self, task: str) -> str:
        """Generates a concise search query from the user's task."""
        prompt = PromptTemplate(
            template="""
You are an expert at summarizing a user's task into a concise search query for finding relevant tools.
The query should capture the main action or intent of the task.

For example:
Task: "Send an email to abc@the-read-example.com with the subject 'Hello'"
Query: "send email"

Task: "Create a new contact in my CRM for John Doe"
Query: "create contact"

Task: "Find the latest news about artificial intelligence"
Query: "search news"

Task: "Post a message to the #general channel in Slack"
Query: "send message"

Task: "{task}"
            """,
            input_variables=["task"],
        )

        class SearchQuery(BaseModel):
            query: str

        response = await self.llm.with_structured_output(SearchQuery).ainvoke(input=prompt.format(task=task))
        query = response.query
        logger.info(f"Generated search query '{query}' for task '{task}'")
        return query

    async def _search_tools(self, state: AgentState) -> AgentState:
        """Searches for and filters tools in the relevant apps."""
        task = state["task"]
        logger.info(f"Searching for tools in relevant apps for task: {task}")
        search_query = await self._generate_search_query(task)
        apps_with_tools = {}
        reasoning_steps = []
        for app_name in state["relevant_apps"]:
            logger.info(f"Searching for tools in {app_name} for task: {task} with query '{search_query}'")
            found_tools = await self.registry.search_tools(query=search_query, app_id=app_name)

            if not found_tools or (len(found_tools) == 1 and found_tools[0]["name"] == "general_purpose_tool"):
                apps_with_tools[app_name] = []
                reasoning_steps.append(f"No specific tools found for '{app_name}' for this task.")
                continue

            selected_tools = await self._select_tools(task, found_tools)
            apps_with_tools[app_name] = selected_tools
            reasoning_steps.append(f"For '{app_name}', selected tool(s): {', '.join(selected_tools)}.")

        return {
            **state,
            "apps_with_tools": apps_with_tools,
            "reasoning": state.get("reasoning", "") + "\n" + "\n".join(reasoning_steps),
        }

    def _handle_no_apps_found(self, state: AgentState) -> AgentState:
        """Handles the case where no relevant apps are found."""
        reasoning = "No suitable application was found among the available apps."
        return {
            **state,
            "apps_with_tools": {},
            "reasoning": state.get("reasoning", "") + "\n" + reasoning,
        }

    async def run(self, task: str) -> dict[str, Any]:
        """Runs the agent for a given task."""
        initial_state = AgentState(
            task=task,
            messages=[HumanMessage(content=task)],
            relevant_apps=[],
            apps_with_tools={},
            apps_required=False,
            reasoning="",
        )
        # The workflow is synchronous
        final_state = await self.workflow.ainvoke(initial_state)
        return final_state


async def main():
    from universal_mcp.agentr.registry import AgentrRegistry
    from universal_mcp.agents.bigtool.utils import load_chat_model

    registry = AgentrRegistry()
    agent = ToolFinderAgent(llm=load_chat_model("gemini/gemini-2.5-flash"), registry=registry)
    result = await agent.run("Send an email to manoj@agentr.dev")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
