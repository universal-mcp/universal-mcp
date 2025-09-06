from typing import Any

import pytest
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from universal_mcp.agents.autoagent import AutoAgent
from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.bigtool import BigToolAgent
from universal_mcp.agents.builder import BuilderAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.planner import PlannerAgent
from universal_mcp.agents.shared.tool_node import build_tool_node_graph
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolFormat


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
                {"id": "send_email", "name": "send_email", "description": "Send an email to a recipient."},
                {"id": "read_email", "name": "read_email", "description": "Read emails from inbox."},
                {"id": "create_draft", "name": "create_draft", "description": "Create a draft email."},
            ],
            "slack": [
                {"id": "send_message", "name": "send_message", "description": "Send a message to a team channel."},
                {"id": "read_channel", "name": "read_channel", "description": "Read messages from a channel."},
            ],
            "google-calendar": [
                {"id": "create_event", "name": "create_event", "description": "Create a new calendar event."},
                {"id": "find_event", "name": "find_event", "description": "Find an event in the calendar."},
            ],
            "github": [
                {"id": "create_issue", "name": "create_issue", "description": "Create an issue in a repository."},
                {"id": "get_issue", "name": "get_issue", "description": "Get details of a specific issue."},
                {"id": "create_pull_request", "name": "create_pull_request", "description": "Create a pull request."},
                {"id": "get_repository", "name": "get_repository", "description": "Get details of a repository."},
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
        tools: list[str],
        format: ToolFormat,
    ) -> list[Any]:
        """Exports a list of mock LangChain tools."""

        @tool
        async def mock_tool_callable(query: str):
            """A mock tool that confirms the task is done."""
            return {"status": "task has been done"}

        # Return a list of mock tools for the ReAct agent to use
        return [mock_tool_callable]

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any]:
        """Call a tool with the given name and arguments."""
        print(f"MockToolRegistry: Called tool '{tool_name}' with args {tool_args}")
        return {"status": f"task has been done by tool {tool_name}"}

    async def list_connected_apps(self) -> list[dict[str, str]]:
        """
        Returns a list of apps that the user has connected/authenticated.
        This is a mock function.
        """
        return [{"app_id": app_id} for app_id in self._connected_apps]


class TestToolFinderGraph:
    @pytest.fixture
    def llm(self):
        return load_chat_model("gemini/gemini-2.5-flash")

    @pytest.fixture
    def registry(self):
        return MockToolRegistry()

    @pytest.mark.asyncio
    async def test_simple_case_connected_app(self, llm, registry):
        """Test Case 1: Simple case (Connected App)"""
        task = "Send an email to my manager about the project update."
        graph = build_tool_node_graph(llm, registry)
        final_state = await graph.ainvoke({"task": task, "messages": [HumanMessage(content=task)]})
        assert final_state["apps_required"] is True
        assert "google-mail" in final_state["relevant_apps"]
        assert "google-mail" in final_state["apps_with_tools"]
        assert "send_email" in final_state["apps_with_tools"]["google-mail"]

    @pytest.mark.asyncio
    async def test_multiple_apps_found(self, llm, registry):
        """Test Case 2: Multiple apps found"""
        task = "Send a message to my team about the new design."
        graph = build_tool_node_graph(llm, registry)
        final_state = await graph.ainvoke({"task": task, "messages": [HumanMessage(content=task)]})
        assert final_state["apps_required"] is True
        assert "google-mail" in final_state["relevant_apps"]
        assert "slack" in final_state["relevant_apps"]
        assert "google-mail" in final_state["apps_with_tools"]
        assert "slack" in final_state["apps_with_tools"]

    @pytest.mark.asyncio
    async def test_no_relevant_app(self, llm, registry):
        """Test Case 3: No relevant app"""
        task = "Can you create a blog post on my wordpress site?"
        graph = build_tool_node_graph(llm, registry)
        final_state = await graph.ainvoke({"task": task, "messages": [HumanMessage(content=task)]})
        assert final_state["apps_required"] is True
        assert not final_state["relevant_apps"]
        assert not final_state["apps_with_tools"]

    @pytest.mark.asyncio
    async def test_multiple_tools_in_one_app(self, llm, registry):
        """Test Case 4: Multiple tools in one app"""
        task = "Create a new issue for a bug in our github repository, and send message on slack about the issue."
        graph = build_tool_node_graph(llm, registry)
        final_state = await graph.ainvoke({"task": task, "messages": [HumanMessage(content=task)]})
        assert final_state["apps_required"] is True
        assert "github" in final_state["relevant_apps"]
        assert "slack" in final_state["relevant_apps"]
        assert "github" in final_state["apps_with_tools"]
        assert "slack" in final_state["apps_with_tools"]
        assert "create_issue" in final_state["apps_with_tools"]["github"]
        assert "send_message" in final_state["apps_with_tools"]["slack"]

    @pytest.mark.asyncio
    async def test_unavailable_app(self, llm, registry):
        """Test Case 5: Unavailable App"""
        task = "Create a new design file in Figma."
        graph = build_tool_node_graph(llm, registry)
        final_state = await graph.ainvoke({"task": task, "messages": [HumanMessage(content=task)]})
        assert final_state["apps_required"] is True
        assert not final_state["relevant_apps"]
        assert not final_state["apps_with_tools"]

    @pytest.mark.asyncio
    async def test_no_app_needed(self, llm, registry):
        """Test Case 6: No App Needed"""
        task = "hello"
        graph = build_tool_node_graph(llm, registry)
        final_state = await graph.ainvoke({"task": task, "messages": [HumanMessage(content=task)]})
        assert final_state["apps_required"] is False


@pytest.mark.parametrize(
    "agent_class",
    [
        AutoAgent,
        BigToolAgent,
        PlannerAgent,
    ],
)
class TestAgents:
    @pytest.fixture
    def agent(self, agent_class: type[BaseAgent]):
        """Set up the test environment for the agent."""
        registry = MockToolRegistry()
        agent = agent_class(
            name=f"Test {agent_class.__name__}",
            instructions="Test instructions",
            model="gemini/gemini-2.5-flash",
            registry=registry,
        )
        return agent

    @pytest.mark.asyncio
    async def test_end_to_end_with_tool(self, agent: BaseAgent):
        """Tests the full flow from task to tool execution."""
        task = "Send an email to my manager."
        thread_id = f"test-thread-{agent.name.replace(' ', '-')}"

        await agent.ainit()
        # Invoke the agent graph to get the final state
        final_state = await agent.invoke(
            task,
            thread_id=thread_id,
        )

        # Extract the content of the last message
        final_messages = final_state.get("messages", [])
        assert final_messages, "The agent should have produced at least one message."
        last_message = final_messages[-1]

        final_response = last_message.content if hasattr(last_message, "content") else str(last_message)

        # Print the response for manual verification and for the LLM judge
        print("\n--- Agent's Final Response ---")
        print(final_response)
        print("------------------------------")

        # Assert that the response is not None or empty, as per the new requirement
        assert final_response is not None, "The final response should not be None."
        assert final_response != "", "The final response should not be an empty string."


class TestAgentBuilder:
    @pytest.fixture
    def agent_builder(self):
        """Set up the agent builder."""
        registry = MockToolRegistry()
        agent = BuilderAgent(
            name="Test Builder Agent",
            instructions="Test instructions for builder",
            model="gemini/gemini-1.5-flash",
            registry=registry,
        )
        yield agent

    @pytest.mark.asyncio
    async def test_create_agent(self, agent_builder: BuilderAgent):
        """Test case for creating an agent with the builder."""
        task = "Send a daily email to manoj@agentr.dev with daily agenda of the day"

        result = await agent_builder.invoke(task)

        assert "generated_agent" in result
        generated_agent = result["generated_agent"]

        assert generated_agent.name
        assert generated_agent.description
        assert generated_agent.expertise
        assert "manoj@agentr.dev" in generated_agent.instructions
        assert generated_agent.schedule is not None

        assert "tool_config" in result
        tool_config = result["tool_config"]
        assert "google-mail" in tool_config
