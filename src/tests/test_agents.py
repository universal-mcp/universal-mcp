import pytest

from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.tool_node import LandGraphAgent, MockToolRegistry


@pytest.fixture
def agent():
    """Set up the test environment."""
    llm = load_chat_model("gemini/gemini-2.5-flash")
    registry = MockToolRegistry()
    return LandGraphAgent(llm, registry)


def test_simple_case_connected_app(agent: LandGraphAgent):
    """Test Case 1: Simple case (Connected App)"""
    task = "Send an email to my manager about the project update."
    result = agent.run(task)
    assert result == {"google-mail": ["send_email"]}


def test_disambiguation(agent: LandGraphAgent):
    """Test Case 2: Disambiguation"""
    task = "Send a message to my team about the new design."
    result = agent.run(task)
    assert "message_to_user" in result
    assert "disambiguation_options" in result
    assert (
        result["message_to_user"]
        == "I found multiple apps that could help: google-mail, slack. Which one would you like to use?"
    )
    assert result["disambiguation_options"] == ["google-mail", "slack"]


def test_no_relevant_app(agent: LandGraphAgent):
    """Test Case 3: No relevant app"""
    task = "Can you create a blog post on my wordpress site?"
    result = agent.run(task)
    assert result == {"message_to_user": "I cannot do this task because the WordPress app is not available."}


def test_multiple_tools_in_one_app(agent: LandGraphAgent):
    """Test Case 4: Multiple tools in one app"""
    task = "Create a new issue for a bug in our github repository, and send message on slack about the issue."
    result = agent.run(task)
    assert result == {"github": ["create_issue"], "slack": ["send_message"]}


def test_unavailable_app(agent: LandGraphAgent):
    """Test Case 5: Unavailable App"""
    task = "Create a new design file in Figma."
    result = agent.run(task)
    assert result == {"message_to_user": "I cannot do this task because the Figma app is not available."}


def test_no_app_needed(agent: LandGraphAgent):
    """Test Case 6: No App Needed"""
    task = "hello"
    result = agent.run(task)
    assert result == {"message_to_user": "No, this is a simple greeting that can be responded to directly."}
