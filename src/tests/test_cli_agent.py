import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock, call # call is not used in snippet, but good to have

from mcp import Message # Assuming mcp.Message is the correct class
from universal_mcp.agents.cli_agent import CLIAgent
# from universal_mcp.client.client import MultiClientServer # For spec if needed

@pytest.fixture
def mock_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # loop.close() # pytest-asyncio usually handles loop cleanup

@pytest.fixture
def mock_mcp_multiclient():
    # CLIAgent currently doesn't actively use mcp_multiclient in its stream_response logic.
    # If it did, this mock would need to be more sophisticated, e.g., MagicMock(spec=MultiClientServer).
    return None

@pytest.mark.asyncio
async def test_cli_agent_init(mock_mcp_multiclient: MagicMock):
    agent_sse_url = "http://fakeagentsse.com/sse"
    agent = CLIAgent(agent_sse_url=agent_sse_url, mcp_multiclient=mock_mcp_multiclient)
    assert agent.agent_sse_url == agent_sse_url
    assert agent.mcp_multiclient is mock_mcp_multiclient # Checks instance, None for now
    assert agent.console is not None

@pytest.mark.asyncio
async def test_cli_agent_stream_response_connection_error(
    mock_mcp_multiclient: MagicMock,
    mock_loop: asyncio.AbstractEventLoop
    ):
    agent_sse_url = "http://unreachable.com/sse"
    agent = CLIAgent(agent_sse_url=agent_sse_url, mcp_multiclient=mock_mcp_multiclient)

    # Patch sse_client to raise ConnectionRefusedError
    with patch('universal_mcp.agents.cli_agent.sse_client', side_effect=ConnectionRefusedError("Test connection error")) as mock_sse_lib_call:
        responses = [resp async for resp in agent.stream_response(user_message="hello", thread_id="thread1")]

    assert len(responses) == 1
    assert responses[0]['type'] == 'error'
    assert "Connection refused" in responses[0]['data']['content']
    # Check that sse_client was called correctly before the error
    mock_sse_lib_call.assert_called_once_with(url=agent_sse_url, headers={}, http_session=None)


@pytest.mark.asyncio
async def test_cli_agent_stream_response_sends_message_and_parses_stream(
    mock_mcp_multiclient: MagicMock,
    mock_loop: asyncio.AbstractEventLoop
    ):
    agent_sse_url = "http://fakeagentsse.com/sse"
    agent = CLIAgent(agent_sse_url=agent_sse_url, mcp_multiclient=mock_mcp_multiclient)

    # Mocking the SSE client and session components used by CLIAgent
    mock_sse_read_stream = AsyncMock()
    mock_sse_write_stream = AsyncMock()

    mock_server_responses = [
        Message(id="msg1", type="on_chat_model_stream", data={"event": "on_chat_model_stream", "data": {"chunk": {"content": "Hello"}}}),
        Message(id="msg2", type="on_chat_model_stream", data={"event": "on_chat_model_stream", "data": {"chunk": {"content": " world"}}}),
        Message(id="msg3", type="stream_end", data={"event": "stream_end", "data": "Finished"}), # Agent should yield this as info
    ]

    current_response_index = 0
    async def read_side_effect():
        nonlocal current_response_index
        if current_response_index < len(mock_server_responses):
            msg = mock_server_responses[current_response_index]
            current_response_index += 1
            await asyncio.sleep(0) # Ensure other tasks can run
            return msg
        # After all messages, simulate a timeout to naturally end the agent's read loop
        raise asyncio.TimeoutError

    # Mock for the mcp.ClientSession instance
    mock_session_instance = MagicMock()
    mock_session_instance.initialize = AsyncMock()
    mock_session_instance._write_message = AsyncMock()
    mock_session_instance._read_message = AsyncMock(side_effect=read_side_effect)

    # Mock for the sse_client async context manager
    # sse_client() returns an object that, when used in 'async with', its __aenter__ returns (read, write)
    mock_sse_client_acm_instance = AsyncMock()
    mock_sse_client_acm_instance.__aenter__.return_value = (mock_sse_read_stream, mock_sse_write_stream)

    # Mock for the mcp.ClientSession async context manager
    # ClientSession() returns an object that, when used in 'async with', its __aenter__ returns mock_session_instance
    mock_client_session_acm_instance = AsyncMock()
    mock_client_session_acm_instance.__aenter__.return_value = mock_session_instance

    # Patch the constructors/functions that return these async context managers
    with patch('universal_mcp.agents.cli_agent.sse_client', return_value=mock_sse_client_acm_instance) as mock_sse_lib_constructor, \
         patch('universal_mcp.agents.cli_agent.ClientSession', return_value=mock_client_session_acm_instance) as mock_session_lib_constructor:

        user_msg = "Tell me a joke"
        thread_id = "thread-joke"

        responses = []
        # Pass http_session=None explicitly if your agent expects it, or ensure kwargs are handled.
        async for resp in agent.stream_response(user_message=user_msg, thread_id=thread_id, http_session=None):
            responses.append(resp)

    # Assertions
    mock_sse_lib_constructor.assert_called_once_with(url=agent_sse_url, headers={}, http_session=None)
    mock_session_lib_constructor.assert_called_once_with(mock_sse_read_stream, mock_sse_write_stream)
    mock_session_instance.initialize.assert_awaited_once()

    mock_session_instance._write_message.assert_awaited_once()
    sent_message_args = mock_session_instance._write_message.call_args[0][0]
    assert isinstance(sent_message_args, Message)
    assert sent_message_args.type == "invoke_agent_stream"
    assert sent_message_args.data['messages'][0]['content'] == user_msg
    assert sent_message_args.data['config']['configurable']['thread_id'] == thread_id

    # _read_message is called for each message + one more time that results in TimeoutError
    assert mock_session_instance._read_message.call_count == len(mock_server_responses) + 1

    assert len(responses) == 4 # "Hello", " world", info for "stream_end", info for "Timeout"
    assert responses[0] == "Hello"
    assert responses[1] == " world"
    assert responses[2]['type'] == 'info'
    assert "Agent stream explicitly finished" in responses[2]['data']['status'] # From stream_end
    assert responses[3]['type'] == 'info'
    assert "Timeout waiting for message" in responses[3]['data']['status'] # From TimeoutError

@pytest.mark.asyncio
async def test_cli_agent_stream_response_handles_error_event(
    mock_mcp_multiclient: MagicMock,
    mock_loop: asyncio.AbstractEventLoop
    ):
    agent_sse_url = "http://fakeagentsse.com/sse"
    agent = CLIAgent(agent_sse_url=agent_sse_url, mcp_multiclient=mock_mcp_multiclient)

    mock_sse_read_stream = AsyncMock()
    mock_sse_write_stream = AsyncMock()

    # Server sends an MCP Message of type "error"
    mock_server_error_response = [
        Message(id="err1", type="error", data={"content": "Something went terribly wrong on server"}),
    ]
    current_response_index = 0
    async def read_side_effect_error():
        nonlocal current_response_index
        if current_response_index < len(mock_server_error_response):
            msg = mock_server_error_response[current_response_index]
            current_response_index += 1
            return msg
        raise asyncio.TimeoutError # To end loop after error message

    mock_session_instance = MagicMock()
    mock_session_instance.initialize = AsyncMock()
    mock_session_instance._write_message = AsyncMock()
    mock_session_instance._read_message = AsyncMock(side_effect=read_side_effect_error)

    mock_sse_client_acm_instance = AsyncMock()
    mock_sse_client_acm_instance.__aenter__.return_value = (mock_sse_read_stream, mock_sse_write_stream)
    mock_client_session_acm_instance = AsyncMock()
    mock_client_session_acm_instance.__aenter__.return_value = mock_session_instance

    with patch('universal_mcp.agents.cli_agent.sse_client', return_value=mock_sse_client_acm_instance), \
         patch('universal_mcp.agents.cli_agent.ClientSession', return_value=mock_client_session_acm_instance):

        responses = [resp async for resp in agent.stream_response("test error", "thread-error", http_session=None)]

    assert len(responses) == 1 # Only the error message should be yielded
    assert responses[0]['type'] == 'error'
    assert responses[0]['data']['content'] == "Something went terribly wrong on server"
    # The loop in agent should break after processing an error type message.
    assert mock_session_instance._read_message.call_count == 1
