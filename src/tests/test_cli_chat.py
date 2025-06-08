import asyncio
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from typer.testing import CliRunner

# Make sure 'app' can be imported. This might require adjusting PYTHONPATH or how 'app' is exposed.
# If src.universal_mcp.cli directly runs app(), we might need to import 'app' carefully.
# For now, assume 'app' is importable from 'universal_mcp.cli'.
from universal_mcp.cli import app as typer_app
from universal_mcp.client.chat_client import RichCLIClient
from mcp.client.session import ClientSession # For spec in mock

runner = CliRunner()

@pytest.fixture
def mock_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture
def mock_rich_cli_client_chat_methods(mock_loop):
    """
    Mocks chat_loop, connect, and disconnect for RichCLIClient.
    Used for testing the CLI command's interaction with the client instance,
    not the client's internal logic.
    """
    with patch('universal_mcp.client.chat_client.RichCLIClient.chat_loop', new_callable=AsyncMock) as mock_chat_loop, \
         patch('universal_mcp.client.chat_client.RichCLIClient.connect', new_callable=AsyncMock, return_value=True) as mock_connect, \
         patch('universal_mcp.client.chat_client.RichCLIClient.disconnect', new_callable=AsyncMock) as mock_disconnect:

        # This fixture is primarily for when the CLI calls methods on an instance of RichCLIClient.
        # The patches are on the class's methods.
        yield {
            "mock_chat_loop": mock_chat_loop,
            "mock_connect": mock_connect,
            "mock_disconnect": mock_disconnect
        }


def test_chat_command_default_url(mock_rich_cli_client_chat_methods):
    """Test that the chat command calls RichCLIClient with the default URL."""
    # Patch the RichCLIClient constructor within the cli module's scope
    with patch('universal_mcp.cli.RichCLIClient', autospec=True) as mock_client_constructor:
        # Configure the mock instance that the constructor will return
        mock_instance = MagicMock(spec=RichCLIClient)
        mock_instance.chat_loop = AsyncMock()
        mock_instance.disconnect = AsyncMock()
        mock_instance.session = True # Simulate an active session for the finally block's disconnect call
        mock_client_constructor.return_value = mock_instance

        result = runner.invoke(typer_app, ["chat"])

        assert result.exit_code == 0, f"CLI exited with {result.exit_code}: {result.stdout}"

        mock_client_constructor.assert_called_once()
        _args, kwargs = mock_client_constructor.call_args
        assert kwargs['server_url'] == "http://localhost:8005/sse"
        mock_instance.chat_loop.assert_awaited_once()


def test_chat_command_custom_url(mock_rich_cli_client_chat_methods):
    """Test that the chat command calls RichCLIClient with a custom URL."""
    custom_url = "http://customserver:1234/sse"
    with patch('universal_mcp.cli.RichCLIClient', autospec=True) as mock_client_constructor:
        mock_instance = MagicMock(spec=RichCLIClient)
        mock_instance.chat_loop = AsyncMock()
        mock_instance.disconnect = AsyncMock()
        mock_instance.session = True
        mock_client_constructor.return_value = mock_instance

        result = runner.invoke(typer_app, ["chat", "--url", custom_url])

        assert result.exit_code == 0, f"CLI exited with {result.exit_code}: {result.stdout}"
        mock_client_constructor.assert_called_once()
        _args, kwargs = mock_client_constructor.call_args
        assert kwargs['server_url'] == custom_url
        mock_instance.chat_loop.assert_awaited_once()


def test_chat_command_servers_json(tmp_path, mock_rich_cli_client_chat_methods):
    """Test that the chat command uses URL from servers.json."""
    servers_content = {"chat_server_url": "http://jsonurl:5678/sse"}
    servers_file = tmp_path / "servers.json"
    with open(servers_file, 'w') as f:
        json.dump(servers_content, f)

    with patch('universal_mcp.cli.RichCLIClient', autospec=True) as mock_client_constructor:
        mock_instance = MagicMock(spec=RichCLIClient)
        mock_instance.chat_loop = AsyncMock()
        mock_instance.disconnect = AsyncMock()
        mock_instance.session = True
        mock_client_constructor.return_value = mock_instance

        result = runner.invoke(typer_app, ["chat", "--servers-json", str(servers_file)])

        assert result.exit_code == 0, f"CLI exited with {result.exit_code}: {result.stdout}"
        mock_client_constructor.assert_called_once()
        _args, kwargs = mock_client_constructor.call_args
        assert kwargs['server_url'] == "http://jsonurl:5678/sse"
        mock_instance.chat_loop.assert_awaited_once()


def test_chat_command_servers_json_fallback(tmp_path, mock_rich_cli_client_chat_methods):
    """Test fallback to default URL if servers.json is invalid or missing key."""
    servers_content = {"wrong_key": "http://jsonurl:5678/sse"} # Missing 'chat_server_url'
    servers_file = tmp_path / "servers.json"
    with open(servers_file, 'w') as f:
        json.dump(servers_content, f)

    default_url = "http://defaultfallback:8005/sse"

    with patch('universal_mcp.cli.RichCLIClient', autospec=True) as mock_client_constructor:
        mock_instance = MagicMock(spec=RichCLIClient)
        mock_instance.chat_loop = AsyncMock()
        mock_instance.disconnect = AsyncMock()
        mock_instance.session = True
        mock_client_constructor.return_value = mock_instance

        result = runner.invoke(typer_app, ["chat", "--servers-json", str(servers_file), "--url", default_url])

        assert result.exit_code == 0, f"CLI exited with {result.exit_code}: {result.stdout}"
        mock_client_constructor.assert_called_once()
        _args, kwargs = mock_client_constructor.call_args
        assert kwargs['server_url'] == default_url
        mock_instance.chat_loop.assert_awaited_once()


@pytest.mark.asyncio
async def test_rich_cli_client_init(mock_loop):
    """Test RichCLIClient initialization."""
    server_url = "http://testurl:1234/sse"
    client = RichCLIClient(server_url=server_url, loop=mock_loop)
    assert client.server_url == server_url
    assert client.loop == mock_loop
    assert client.session is None
    assert client.console is not None
    assert client.exit_stack is not None


@pytest.mark.asyncio
async def test_rich_cli_client_connect_disconnect(mock_loop):
    """Test connect and disconnect methods (mocking actual SSE calls)."""
    server_url = "http://testurl:1234/sse"
    client = RichCLIClient(server_url=server_url, loop=mock_loop)

    mock_read_stream = AsyncMock()
    mock_write_stream = AsyncMock()

    # sse_client itself is an async context manager
    mock_sse_client_acm = AsyncMock()
    # __aenter__ of sse_client's returned object should yield (read, write)
    mock_sse_client_acm.__aenter__.return_value = (mock_read_stream, mock_write_stream)

    # ClientSession is also an async context manager
    mock_client_session_acm = AsyncMock()
    mock_session_instance = AsyncMock(spec=ClientSession) # Mock the instance returned by ClientSession's __aenter__
    mock_session_instance.initialize = AsyncMock()
    mock_client_session_acm.__aenter__.return_value = mock_session_instance

    # Patch the call that returns the async context manager
    with patch('mcp.client.sse.sse_client', return_value=mock_sse_client_acm) as mock_sse_lib_call, \
         patch('universal_mcp.client.chat_client.ClientSession', return_value=mock_client_session_acm) as mock_session_lib_constructor:

        connected = await client.connect()
        assert connected is True
        assert client.session is mock_session_instance # Ensure the instance from ClientSession's context is assigned

        mock_sse_lib_call.assert_called_once_with(url=server_url, headers={})
        # Ensure ClientSession constructor was called with the streams from sse_client
        mock_session_lib_constructor.assert_called_once_with(mock_read_stream, mock_write_stream)
        mock_session_instance.initialize.assert_awaited_once()

        await client.disconnect()
        # exit_stack.aclose() calls __aexit__ on registered context managers
        mock_sse_client_acm.__aexit__.assert_awaited_once()
        mock_client_session_acm.__aexit__.assert_awaited_once()
        # If client.session was reset or other cleanup, test that too
        # For now, just testing that the contexts were exited.
