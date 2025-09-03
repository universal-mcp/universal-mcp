# tool_node.py

import asyncio
import operator
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, StateGraph

from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig, ToolFormat


class MockToolRegistry(ToolRegistry):
    """Mock implementation of ToolRegistry with an interface compatible with AgentrRegistry."""

    def __init__(self, **kwargs: Any):
        """Initialize the MockToolRegistry."""
        self._apps = [
            {"id": "google-mail", "name": "google-mail", "description": "Send and manage emails."},
            {"id": "slack", "name": "slack", "description": "Team communication and messaging."},
            {
                "id": "google-calendar",
                "name": "google-calendar",
                "description": "Schedule and manage calendar events.",
            },
            {"id": "jira", "name": "jira", "description": "Project tracking and issue management."},
            {
                "id": "github",
                "name": "github",
                "description": "Code hosting, version control, and collaboration.",
            },
        ]
        self._connected_apps = ["google-mail", "google-calendar", "github"]
        self._tools = {
            "google-mail": [
                {"name": "send_email", "description": "Send an email to a recipient."},
                {"name": "read_email", "description": "Read emails from inbox."},
                {"name": "create_draft", "description": "Create a draft email."},
            ],
            "slack": [
                {"name": "send_message", "description": "Send a message to a team channel."},
                {"name": "read_channel", "description": "Read messages from a channel."},
            ],
            "google-calendar": [
                {"name": "create_event", "description": "Create a new calendar event."},
                {"name": "find_event", "description": "Find an event in the calendar."},
            ],
            "github": [
                {"name": "create_issue", "description": "Create an issue in a repository."},
                {"name": "get_issue", "description": "Get details of a specific issue."},
                {"name": "create_pull_request", "description": "Create a pull request."},
                {"name": "get_repository", "description": "Get details of a repository."},
            ],
        }
        self._tool_mappings = {
            "google-mail": {
                "email": ["send_email", "read_email", "create_draft"],
                "send": ["send_email"],
            },
            "slack": {
                "message": ["send_message", "read_channel"],
                "team": ["send_message"],
            },
            "google-calendar": {
                "meeting": ["create_event", "find_event"],
                "schedule": ["create_event"],
            },
            "github": {
                "issue": ["create_issue", "get_issue"],
                "code": ["create_pull_request", "get_repository"],
            },
        }

    async def list_all_apps(self) -> list[dict[str, Any]]:
        """Get list of available apps."""
        return self._apps

    async def get_app_details(self, app_id: str) -> dict[str, Any]:
        """Get detailed information about a specific app."""
        for app in self._apps:
            if app["id"] == app_id:
                return app
        return {}

    async def search_apps(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for apps by a query."""
        query = query.lower()
        results = [app for app in self._apps if query in app["name"].lower() or query in app["description"].lower()]
        return results[:limit]

    async def list_tools(
        self,
        app_id: str,
    ) -> list[dict[str, Any]]:
        """List all tools available for a specific app."""
        return self._tools.get(app_id, [])

    async def search_tools(
        self,
        query: str,
        limit: int = 10,
        app_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for tools by a query."""
        if not app_id:
            return []

        tools_for_app = self._tool_mappings.get(app_id, {})
        found_tool_names = set()
        for keyword, tools in tools_for_app.items():
            if keyword in query.lower():
                for tool in tools:
                    found_tool_names.add(tool)

        all_app_tools = self._tools.get(app_id, [])

        results = [tool for tool in all_app_tools if tool["name"] in found_tool_names]

        if not results:
            results = [{"name": "general_purpose_tool", "description": "A general purpose tool."}]

        return results[:limit]

    async def export_tools(
        self,
        tools: list[str] | ToolConfig,
        format: ToolFormat,
    ) -> str:
        """Export given tools to required format."""
        return f"Exported {tools} in {format} format."

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any]:
        """Call a tool with the given name and arguments."""
        return {"result": f"Called tool {tool_name} with args {tool_args}"}

    def list_connected_apps(self) -> list[str]:
        """
        Returns a list of apps that the user has connected/authenticated.
        This is a mock function.
        """
        return self._connected_apps


# --- LangGraph Agent ---


class AgentState(TypedDict):
    task: str
    messages: Annotated[list[AnyMessage], operator.add]
    result: dict[str, Any]
    relevant_apps: list[str]
    apps_required: bool


class LandGraphAgent:
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
        workflow.add_node("handle_disambiguation", self._handle_disambiguation)
        workflow.add_node("handle_no_apps_found", self._handle_no_apps_found)

        workflow.set_entry_point("check_if_app_needed")

        workflow.add_conditional_edges(
            "check_if_app_needed",
            lambda state: "find_relevant_apps" if state.get("apps_required") else END,
        )
        workflow.add_conditional_edges(
            "find_relevant_apps",
            self._decide_next_step,
            {
                "search": "search_tools",
                "disambiguate": "handle_disambiguation",
                "end": "handle_no_apps_found",
            },
        )

        workflow.add_edge("search_tools", END)
        workflow.add_edge("handle_disambiguation", END)
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

        if content.lower().startswith("yes"):
            return {**state, "messages": [AIMessage(content=content)], "apps_required": True, "relevant_apps": []}
        else:
            return {
                **state,
                "messages": [AIMessage(content=content)],
                "result": {"message_to_user": content},
                "apps_required": False,
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

        if app_list:
            message = f"I've identified the following relevant app(s): {', '.join(app_list)}."
            return {**state, "messages": [AIMessage(content=message)], "relevant_apps": app_list}

        return {**state, "relevant_apps": app_list}

    def _decide_next_step(self, state: AgentState) -> str:
        """Decides the next step based on the number of relevant apps found."""
        if not state["relevant_apps"]:
            return "end"
        if len(state["relevant_apps"]) == 1:
            return "search"

        task = state["task"]
        apps = state["relevant_apps"]
        prompt = PromptTemplate(
            template="""
            Given the user's task: "{task}"
            And the list of relevant apps: {apps}

            Does the task require the user to CHOOSE ONE of these apps, or does it require using MULTIPLE of them to be fully completed?
            Respond with the single word "CHOOSE" or "MULTIPLE".
            """,
            input_variables=["task", "apps"],
        )
        chain = prompt | self.llm
        response = chain.invoke({"task": task, "apps": ", ".join(apps)})

        return "search" if "MULTIPLE" in response.content.upper() else "disambiguate"

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
        final_result = {}
        messages = []
        for app_name in state["relevant_apps"]:
            messages.append(AIMessage(content=f"Searching for tools in '{app_name}'..."))
            found_tools_dicts = asyncio.run(self.registry.search_tools(query=task, app_id=app_name))
            found_tools = [tool["name"] for tool in found_tools_dicts]

            if not found_tools or (len(found_tools) == 1 and found_tools[0] == "general_purpose_tool"):
                final_result[app_name] = []
                messages.append(AIMessage(content=f"No specific tools found for '{app_name}' for this task."))
                continue

            filtered_tools = self._filter_tools(task, app_name, found_tools)
            final_result[app_name] = filtered_tools

            if filtered_tools:
                messages.append(
                    AIMessage(
                        content=f"For '{app_name}', I've selected the following tool(s): {', '.join(filtered_tools)}."
                    )
                )
            else:
                messages.append(
                    AIMessage(content=f"Found some tools in '{app_name}', but none seem right for this specific task.")
                )

        return {**state, "messages": messages, "result": final_result}

    def _handle_no_apps_found(self, state: AgentState) -> AgentState:
        """Handles the case where no relevant apps are found."""
        task = state["task"]
        all_apps = asyncio.run(self.registry.list_all_apps())
        all_apps_str = ", ".join([app["name"] for app in all_apps])
        prompt = PromptTemplate(
            template="""
            The user's task is: "{task}".
            No suitable application was found among the available apps: {all_apps}.

            Generate a user-facing message explaining why the task cannot be completed.
            - If the task explicitly mentions an application that is not in the available list, the message should state that the specific app is not available. For example: "I cannot do this task because the Figma app is not available."
            - Otherwise, provide a more general message. For example: "I cannot do this task because no suitable application was found."
            """,
            input_variables=["task", "all_apps"],
        )
        chain = prompt | self.llm
        response = chain.invoke({"task": task, "all_apps": all_apps_str})
        message = response.content.strip()
        return {**state, "messages": [AIMessage(content=message)], "result": {"message_to_user": message}}

    def _handle_disambiguation(self, state: AgentState) -> AgentState:
        """Asks the user to choose from multiple relevant apps."""
        apps = state["relevant_apps"]
        message = f"I found multiple apps that could help: {', '.join(apps)}. Which one would you like to use?"
        return {
            **state,
            "result": {"message_to_user": message, "disambiguation_options": apps},
            "messages": [AIMessage(content=message)],
        }

    def run(self, task: str) -> dict[str, list[str]]:
        """Runs the agent for a given task."""
        initial_state = AgentState(
            task=task,
            messages=[HumanMessage(content=task)],
            result={},
            relevant_apps=[],
            apps_required=True,
        )
        final_state = self.workflow.invoke(initial_state)
        return final_state.get("result", {})
