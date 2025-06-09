# src/universal_mcp/agents/cli_agent.py
import asyncio
import uuid
from typing import AsyncGenerator, Union, Dict, Any, Optional

from mcp import ClientSession, Message # Assuming mcp.Message is correct
from mcp.client.sse import sse_client
from rich.console import Console # For potential logging or errors from agent itself

from universal_mcp.agents.base import Agent

# Forward declaration for MultiClientServer for type hinting if it's not directly used
# or to avoid circular imports if it were to use agents.
# If MultiClientServer is defined in a place that can be cleanly imported, that's better.
# from universal_mcp.client.client import MultiClientServer # Example if it's importable
class MultiClientServer:
    pass


class CLIAgent(Agent):
    """
    An agent designed for CLI interaction, communicating with a language model
    or other backend via an SSE endpoint.
    """

    def __init__(self, agent_sse_url: str, mcp_multiclient: Optional[MultiClientServer] = None):
        """
        Initializes the CLIAgent.

        Args:
            agent_sse_url: The URL of the agent's or language model's SSE endpoint.
            mcp_multiclient: An optional MultiClientServer instance if this agent
                             needs to directly call other tools/services via MCP.
                             (Not used in this specific agent's core streaming logic).
        """
        self.agent_sse_url = agent_sse_url
        self.mcp_multiclient = mcp_multiclient
        self.console = Console(stderr=True) # Use stderr for agent's own logs/errors

    async def stream_response(
        self,
        user_message: str,
        thread_id: str,
        **kwargs: Any # e.g., http_session from RichCLIClient if needed by sse_client
    ) -> AsyncGenerator[Union[str, Dict[str, Any]], None]:
        """
        Connects to the agent's SSE endpoint, sends the user message,
        and streams back the response.
        """

        exit_stack = asyncio.AsyncExitStack()
        session: Optional[ClientSession] = None

        try:
            # Establish SSE connection for this stream interaction
            try:
                # self.console.log(f"[CLIAgent] Attempting to connect to: {self.agent_sse_url}")
                # Pass http_session if provided and sse_client supports it
                current_http_session = kwargs.get("http_session")
                read, write = await exit_stack.enter_async_context(
                    sse_client(url=self.agent_sse_url, headers={}, http_session=current_http_session)
                )
                session = await exit_stack.enter_async_context(
                    ClientSession(read, write)
                )
                await session.initialize()
                # self.console.log(f"[CLIAgent] Connected to {self.agent_sse_url}")
            except ConnectionRefusedError:
                yield {"type": "error", "data": {"content": f"Connection refused to agent SSE server at {self.agent_sse_url}."}}
                return
            except Exception as e:
                # self.console.print_exception(show_locals=True) # For debugging agent-side
                yield {"type": "error", "data": {"content": f"CLIAgent failed to connect to SSE endpoint '{self.agent_sse_url}': {type(e).__name__} - {e}"}}
                return

            if not session: # Should ideally be caught by previous exception handling
                yield {"type": "error", "data": {"content": "Agent SSE session not established."}}
                return

            # 1. Send user message
            message_id = str(uuid.uuid4())
            # This payload structure is speculative and needs to match what the target SSE agent expects.
            # It's common for agents using LangGraph or similar frameworks.
            payload = {
                "messages": [{"role": "user", "content": user_message}], # LangChain/LangGraph style input
                "config": {"configurable": {"thread_id": thread_id}},   # For stateful LangGraph agents
            }
            # The 'type' of this message is also speculative.
            # "invoke_agent_stream" implies we want the agent to process and stream back.
            # Other possibilities: "chat_message_request", "process_input_stream"
            mcp_message_to_send = Message(
                id=message_id,
                type="invoke_agent_stream",
                data=payload,
                source="cli_agent" # Optional field for clarity
            )
            await session._write_message(mcp_message_to_send)
            # yield {"type": "info", "data": {"status": "Message sent to agent, awaiting stream..."}}


            # 2. Receive and process streamed messages
            while True:
                try:
                    received_mcp_message: Message = await asyncio.wait_for(session._read_message(), timeout=60.0)

                    if not received_mcp_message: # Should be caught by timeout, but good to have
                        yield {"type": "info", "data": {"status": "Stream ended (no further message received)."}}
                        break

                    event_data = received_mcp_message.data
                    event_type = received_mcp_message.type

                    # Attempt to interpret nested event structure (common with LangGraph)
                    inner_event_type = None
                    inner_event_name = None # For LangGraph's "event" field like "on_chat_model_stream"
                    parsed_data = event_data # Default to using event_data directly

                    if isinstance(event_data, dict):
                        inner_event_name = event_data.get("event") # e.g. "on_chat_model_stream"
                        if inner_event_name: # If it's a LangGraph-like nested event
                            parsed_data = event_data.get("data", {}) # The actual content is in "data" field
                        # If no inner_event_name, parsed_data remains event_data (the whole dict)

                    # Determine the most specific event type we have
                    effective_event_type = inner_event_name or event_type

                    # self.console.log(f"Msg Type: {event_type}, Effective Type: {effective_event_type}, Parsed Data: {parsed_data}")

                    if effective_event_type == "on_chat_model_stream" and isinstance(parsed_data, dict):
                        # Standard LangGraph stream chunk for LLMs
                        chunk_obj = parsed_data.get("chunk", {})
                        if isinstance(chunk_obj, dict): # Chunk is often a AIMessageChunk or HumanMessageChunk like object
                            chunk_content = chunk_obj.get("content", "")
                            if chunk_content: yield str(chunk_content)
                        elif isinstance(chunk_obj, str): # Simpler chunk
                             if chunk_obj: yield chunk_obj
                    elif effective_event_type in ("on_tool_start", "on_tool_stream", "on_tool_end") and isinstance(parsed_data, dict):
                        yield {"type": "tool_event", "event_name": effective_event_type, "data": parsed_data}
                    elif effective_event_type == "on_chain_end" or effective_event_type == "on_graph_end":
                         # These are often just signals, actual content might have already been streamed.
                         # Could yield an info message if desired:
                         # yield {"type": "info", "data": {"status": f"{effective_event_type} received."}}
                         pass # Or simply do nothing if no specific output is expected here.
                    elif event_type == "token_chunk" and isinstance(event_data, dict): # A more generic token type
                        chunk = event_data.get("text", "")
                        if chunk: yield str(chunk)
                    elif event_type == "stream_end" or event_type == "agent_response_end": # Explicit stream end from server
                        yield {"type": "info", "data": {"status": "Agent stream explicitly finished."}}
                        break
                    elif event_type == "error":
                        error_content = parsed_data.get("content", parsed_data.get("message", "Unknown error from agent")) if isinstance(parsed_data, dict) else str(parsed_data)
                        yield {"type": "error", "data": {"content": error_content}}
                        break
                    elif isinstance(parsed_data, dict) and parsed_data: # Yield unhandled dicts as structured messages
                         yield {"type": "structured_message", "event_type": effective_event_type, "data": parsed_data}
                    elif isinstance(parsed_data, str) and parsed_data : # Yield unhandled strings if they are the data
                        yield parsed_data
                    # else:
                        # Optionally yield unknown/unhandled message types for debugging by the receiver
                        # yield {"type": "unknown_event", "original_type": event_type, "original_data": event_data}

                except asyncio.TimeoutError:
                    yield {"type": "info", "data": {"status": "Timeout waiting for message from agent. Stream might have ended."}}
                    break
                except Exception as e:
                    # self.console.print_exception(show_locals=True) # For debugging agent-side
                    yield {"type": "error", "data": {"content": f"CLIAgent error processing message from agent: {type(e).__name__} - {e}"}}
                    break

        except Exception as e: # Catch errors from initial connection or message sending
            # self.console.print_exception(show_locals=True) # For debugging agent-side
            yield {"type": "error", "data": {"content": f"CLIAgent stream_response failed before or during stream loop: {type(e).__name__} - {e}"}}
        finally:
            # Ensure SSE connection is closed
            # self.console.log("[CLIAgent] Closing SSE connection.")
            await exit_stack.aclose()
