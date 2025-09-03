# tool_node.py

import asyncio
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from universal_mcp.tools.registry import ToolRegistry

# --- LangGraph Agent ---


class AgentState(TypedDict):
    task: str
    apps_required: bool
    apps_with_tools: dict[str, list[str]]
    relevant_apps: list[str]
    messages: Annotated[list[AnyMessage], add_messages]
    reasoning: str


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

    def _find_relevant_apps(self, state: AgentState) -> AgentState:
        """Identifies relevant apps for the given task, preferring connected apps."""
        task = state["task"]
        all_apps = asyncio.run(self.registry.list_all_apps())
        connected_apps = self.registry.list_connected_apps()
        prompt = PromptTemplate(
            template="""
            Given the user's task: "{task}"
            And the list of all available apps: {all_apps}
            And the list of apps the user has connected: {connected_apps}

            Identify all possible relevant app(s) for the task, considering the task description and the app descriptions. Prefer connected apps.
            Return a comma-separated list of app names. For example: google-mail,slack
            If no app is relevant, return "None".
            """,
            input_variables=["task", "all_apps", "connected_apps"],
        )
        chain = prompt | self.llm
        response = chain.invoke(
            {
                "task": task,
                "all_apps": all_apps,
                "connected_apps": connected_apps,
            }
        )
        app_list = [app.strip() for app in response.content.split(",") if app.strip() and app.strip().lower() != "none"]
        reasoning = f"Found relevant apps: {app_list}. LLM response: {response.content}"

        return {
            **state,
            "messages": [AIMessage(content=f"Identified relevant apps: {', '.join(app_list)}")],
            "relevant_apps": app_list,
            "reasoning": state.get("reasoning", "") + "\n" + reasoning,
        }

    def _filter_tools(self, task: str, app_name: str, tools: list[str]) -> list[str]:
        """Filters a list of tools based on the task."""
        prompt = PromptTemplate(
            template="""
            Given the user's task: "{task}"
            And the following list of available tools for the app '{app_name}': {tools}

            Select the minimal set of tools from this list required to complete the part of the task relevant to this app.
            Return a comma-separated list of tool names. For example: send_email,create_draft
            If no tool is relevant, return "None".
            """,
            input_variables=["task", "app_name", "tools"],
        )
        chain = prompt | self.llm
        response = chain.invoke({"task": task, "app_name": app_name, "tools": ", ".join(tools)})
        return [tool.strip() for tool in response.content.split(",") if tool.strip() and tool.strip().lower() != "none"]

    def _search_tools(self, state: AgentState) -> AgentState:
        """Searches for and filters tools in the relevant apps."""
        task = state["task"]
        apps_with_tools = {}
        reasoning_steps = []
        for app_name in state["relevant_apps"]:
            found_tools_dicts = asyncio.run(self.registry.search_tools(query=task, app_id=app_name))
            found_tools = [tool["name"] for tool in found_tools_dicts]

            if not found_tools or (len(found_tools) == 1 and found_tools[0] == "general_purpose_tool"):
                apps_with_tools[app_name] = []
                reasoning_steps.append(f"No specific tools found for '{app_name}' for this task.")
                continue

            filtered_tools = self._filter_tools(task, app_name, found_tools)
            apps_with_tools[app_name] = filtered_tools
            reasoning_steps.append(f"For '{app_name}', selected tool(s): {', '.join(filtered_tools)}.")

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

    def run(self, task: str) -> dict[str, Any]:
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
        final_state = self.workflow.invoke(initial_state)
        return final_state
