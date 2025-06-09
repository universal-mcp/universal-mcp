# src/tests/test_cli_chat.py
import asyncio
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock, ANY

import pytest
from typer.testing import CliRunner

from universal_mcp.cli import app as typer_app
from universal_mcp.client.chat_client import RichCLIClient
from universal_mcp.agents.base import Agent # For type hinting mock agent
from universal_mcp.agents.cli_agent import CLIAgent # For spec in mock
from universal_mcp.client.client import MultiClientServer # For spec in mock
from universal_mcp.config import ClientTransportConfig # For spec in mock

runner = CliRunner()

@pytest.fixture
def mock_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # loop.close() # Closing the loop can cause issues with other async tests if not managed carefully.
                  # pytest-asyncio normally handles loop cleanup.

# Updated tests for the CLI command
@patch('universal_mcp.cli.RichCLIClient', autospec=True)
@patch('universal_mcp.cli.CLIAgent', autospec=True)
@patch('universal_mcp.cli.MultiClientServer', autospec=True)
def test_chat_command_default_url(
    mock_multi_client_server_constructor: MagicMock,
    mock_cli_agent_constructor: MagicMock,
    mock_rich_cli_client_constructor: MagicMock,
    mock_loop: asyncio.AbstractEventLoop # Ensure loop fixture is used if tests involve async aspects implicitly
    ):
    mock_agent_instance = MagicMock(spec=CLIAgent)
    mock_cli_agent_constructor.return_value = mock_agent_instance

    mock_ui_instance = MagicMock(spec=RichCLIClient)
    mock_ui_instance.chat_loop = AsyncMock() # chat_loop is called by cli
    mock_rich_cli_client_constructor.return_value = mock_ui_instance

    result = runner.invoke(typer_app, ["chat"])

    assert result.exit_code == 0, f"CLI Error: {result.stdout}"
    mock_cli_agent_constructor.assert_called_once_with(
        agent_sse_url="http://localhost:8005/sse",
        mcp_multiclient=None # No tool_servers by default
    )
    mock_rich_cli_client_constructor.assert_called_once_with(agent=mock_agent_instance)
    mock_ui_instance.chat_loop.assert_awaited_once()
    mock_multi_client_server_constructor.assert_not_called()


@patch('universal_mcp.cli.RichCLIClient', autospec=True)
@patch('universal_mcp.cli.CLIAgent', autospec=True)
@patch('universal_mcp.cli.MultiClientServer', autospec=True)
def test_chat_command_custom_agent_url(
    mock_multi_client_server_constructor: MagicMock,
    mock_cli_agent_constructor: MagicMock,
    mock_rich_cli_client_constructor: MagicMock,
    mock_loop: asyncio.AbstractEventLoop
    ):
    custom_url = "http://customagent:1234/sse"
    mock_agent_instance = MagicMock(spec=CLIAgent)
    mock_cli_agent_constructor.return_value = mock_agent_instance
    mock_ui_instance = MagicMock(spec=RichCLIClient)
    mock_ui_instance.chat_loop = AsyncMock()
    mock_rich_cli_client_constructor.return_value = mock_ui_instance

    result = runner.invoke(typer_app, ["chat", "--url", custom_url])

    assert result.exit_code == 0, f"CLI Error: {result.stdout}"
    mock_cli_agent_constructor.assert_called_once_with(
        agent_sse_url=custom_url,
        mcp_multiclient=None
    )
    mock_rich_cli_client_constructor.assert_called_once_with(agent=mock_agent_instance)
    mock_ui_instance.chat_loop.assert_awaited_once()
    mock_multi_client_server_constructor.assert_not_called()


@patch('universal_mcp.cli.RichCLIClient', autospec=True)
@patch('universal_mcp.cli.CLIAgent', autospec=True)
@patch('universal_mcp.cli.MultiClientServer', autospec=True)
@patch('universal_mcp.cli.ClientTransportConfig', autospec=True) # Mock the config class itself
def test_chat_command_servers_json_with_agent_and_tools(
    mock_client_transport_config_constructor: MagicMock,
    mock_multi_client_server_constructor: MagicMock,
    mock_cli_agent_constructor: MagicMock,
    mock_rich_cli_client_constructor: MagicMock,
    tmp_path: Path,
    mock_loop: asyncio.AbstractEventLoop
):
    agent_json_url = "http://jsonagent:5678/sse"
    tool_server_url = "http://toolserver1:8006/mcp"
    tool_server_config_dict = {"url": tool_server_url, "transport": "sse", "name": "server1"}
    servers_content = {
        "agent_sse_url": agent_json_url,
        "tool_servers": {
            "server1": tool_server_config_dict
        }
    }
    servers_file = tmp_path / "servers.json"
    with open(servers_file, 'w') as f:
        json.dump(servers_content, f)

    mock_agent_instance = MagicMock(spec=CLIAgent)
    mock_cli_agent_constructor.return_value = mock_agent_instance
    mock_ui_instance = MagicMock(spec=RichCLIClient)
    mock_ui_instance.chat_loop = AsyncMock()
    mock_rich_cli_client_constructor.return_value = mock_ui_instance

    # This mock represents an instance of ClientTransportConfig
    mock_transport_config_instance = MagicMock(spec=ClientTransportConfig)
    # Make the constructor return this mock instance
    mock_client_transport_config_constructor.return_value = mock_transport_config_instance

    mock_mcp_multiclient_instance = MagicMock(spec=MultiClientServer)
    mock_multi_client_server_constructor.return_value = mock_mcp_multiclient_instance


    result = runner.invoke(typer_app, ["chat", "--servers-json", str(servers_file)])

    assert result.exit_code == 0, f"CLI Error: {result.stdout}"

    # Check ClientTransportConfig instantiation
    # Pydantic models take kwargs, so use that for assertion
    mock_client_transport_config_constructor.assert_called_once_with(**tool_server_config_dict)

    # Check MultiClientServer instantiation
    mock_multi_client_server_constructor.assert_called_once_with(
        clients={"server1": mock_transport_config_instance}
    )

    # Check CLIAgent instantiation
    mock_cli_agent_constructor.assert_called_once_with(
        agent_sse_url=agent_json_url,
        mcp_multiclient=mock_mcp_multiclient_instance
    )
    mock_rich_cli_client_constructor.assert_called_once_with(agent=mock_agent_instance)
    mock_ui_instance.chat_loop.assert_awaited_once()


# Updated RichCLIClient unit tests
@pytest.mark.asyncio
async def test_rich_cli_client_init(mock_loop: asyncio.AbstractEventLoop):
    mock_agent = MagicMock(spec=Agent) # Use the base Agent for spec
    client = RichCLIClient(agent=mock_agent, loop=mock_loop)
    assert client.agent is mock_agent
    assert client.loop is mock_loop
    assert client.console is not None

@pytest.mark.asyncio
async def test_rich_cli_client_chat_loop_calls_agent(mock_loop: asyncio.AbstractEventLoop):
    mock_agent = MagicMock(spec=Agent)

    # Make stream_response an async generator mock
    async def mock_stream_response_gen(*args, **kwargs):
        yield "Hello "
        yield {"type": "info", "data": {"status": "Processing..."}}
        yield "World"
        yield {"type": "info", "data": {"status": "Stream ended"}}

    # Assign the generator function to be the side_effect of the mock method
    mock_agent.stream_response = MagicMock(side_effect=mock_stream_response_gen)

    client = RichCLIClient(agent=mock_agent, loop=mock_loop)

    # Mock console.input_async to return a value and then raise EOFError to stop the loop
    with patch.object(client.console, 'input_async', new_callable=AsyncMock) as mock_input:
        mock_input.side_effect = ["Test message", EOFError("Simulate Ctrl+D")]

        # Mock rich.live.Live context manager and its update method
        # The Live instance itself is the context manager
        mock_live_cm = MagicMock() # This will be returned by Live()
        mock_live_cm.update = MagicMock() # Method on the context manager instance
        mock_live_cm.__enter__.return_value = mock_live_cm # __enter__ returns the context manager itself
        mock_live_cm.__aenter__.return_value = mock_live_cm # For async with, though Live is sync

        with patch('universal_mcp.client.chat_client.Live', return_value=mock_live_cm) as mock_live_constructor:
            await client.chat_loop()

    mock_input.assert_called_once_with(ANY) # Check that input was called at least once
    mock_agent.stream_response.assert_called_once_with(user_message="Test message", thread_id=ANY)

    # Check that Live was constructed and updated
    mock_live_constructor.assert_called_once()
    # Expected updates: initial panel, then for each of the 4 yields.
    assert mock_live_cm.update.call_count >= 4
