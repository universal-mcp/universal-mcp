import asyncio
import uuid
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from mcp import Message # Assuming mcp.Message is correct

# Placeholder for actual MCPClient if needed for direct use,
# but for now, we'll focus on sse_client and ClientSession
# from universal_mcp.client.client import MCPClient
# from universal_mcp.config import ClientTransportConfig, SSETransportConfig # Not used for now


class RichCLIClient:
    def __init__(self, server_url: str, loop: asyncio.AbstractEventLoop):
        self.server_url = server_url
        self.loop = loop
        self.session: Optional[ClientSession] = None
        self.exit_stack = asyncio.AsyncExitStack()
        self.console = Console()
        # If using MCPClient directly (not for this initial setup):
        # transport_config = SSETransportConfig(url=server_url, transport="sse")
        # self.mcp_client = MCPClient(name="cli_chat_client", config=transport_config)

    async def connect(self):
        self.console.print(f"Attempting to connect to {self.server_url}...")
        try:
            # We will use the sse_client directly as per playground examples for streaming
            # The headers might be needed for authentication tokens if the server requires them.
            read, write = await self.exit_stack.enter_async_context(
                sse_client(url=self.server_url, headers={})
            )
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            # Perform the handshake with the server. This is crucial.
            await self.session.initialize()
            self.console.print(f"[green]Successfully connected to {self.server_url}[/green]")
            return True
        except ConnectionRefusedError:
            self.console.print(f"[red]Connection refused. Ensure the server is running at {self.server_url}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]Failed to connect: {e}[/red]")
            # Consider logging the full traceback for debugging
            # import traceback
            # self.console.print(traceback.format_exc())
            return False

    async def disconnect(self):
        self.console.print("Disconnecting...")
        await self.exit_stack.aclose()
        self.console.print("[bold yellow]Disconnected.[/bold yellow]")

    async def simulate_send_and_receive(self, text: str, thread_id: str) -> str:
        """
        Simulates sending a message and receiving a full response.
        In a real scenario, this would involve network communication and actual streaming.
        For now, it just echoes the input.
        """
        if not self.session:
            self.console.print("[red]Not connected (simulation error).[/red]")
            return "Error: Not connected."

        # Simulate network delay and processing
        await asyncio.sleep(0.5)
        return f"Echo from AI ({thread_id}): {text}"

    async def send_and_stream_response(self, user_message: str, thread_id: str, live_display: Live, text_area: Text):
        if not self.session:
            text_area.append("[red]Error: Not connected.[/red]")
            live_display.update(Panel(text_area, title="[bold red]AI - Error[/bold red]", border_style="red", expand=False))
            return

        try:
            message_id = str(uuid.uuid4())
            payload = {
                "messages": [{"role": "user", "content": user_message}],
                "config": {"configurable": {"thread_id": thread_id}},
            }

            # Speculative message type for invoking an agent that streams back.
            # This needs to match what the MCP server's agent setup expects.
            mcp_message_to_send = Message(
                id=message_id,
                type="invoke_agent_stream",
                data=payload,
                source="cli_chat_client", # Optional: identify the sender
                # target="agent_service" # Optional: if routing is needed and supported
            )

            # Clear previous AI response area if desired, or append
            # text_area.plain = "" # Clears the Text object
            text_area.append(Text.from_markup("[grey50]Sending message...[/grey50]\n"))
            live_display.update(Panel(text_area, title="[bold green]AI[/bold green]", border_style="green", expand=False))

            await self.session._write_message(mcp_message_to_send)

            while True:
                try:
                    received_mcp_message: Message = await asyncio.wait_for(self.session._read_message(), timeout=60.0)

                    if not received_mcp_message:
                        text_area.append("\n[yellow]Stream ended (no further message).[/yellow]")
                        break

                    event_data = received_mcp_message.data
                    event_type = received_mcp_message.type # Primary type from MCP Message

                    # Secondary event type, if data payload itself contains an "event" field (e.g. LangGraph events)
                    # This is common if MCP server just relays events from an underlying agent framework.
                    if isinstance(event_data, dict) and "event" in event_data:
                        inner_event_type = event_data.get("event")
                        inner_event_data = event_data.get("data", {})
                    else: # Assume event_data is the direct payload if no inner "event" field
                        inner_event_type = event_type
                        inner_event_data = event_data

                    # Example log for debugging server messages
                    # self.console.log(f"Received MCP Msg Type: {event_type}, Data: {event_data}")
                    # self.console.log(f"Interpreted Event Type: {inner_event_type}, Data: {inner_event_data}")

                    if inner_event_type == "on_chat_model_stream" and isinstance(inner_event_data, dict):
                        # Standard LangGraph stream chunk for LLMs
                        chunk = inner_event_data.get("chunk", "")
                        if isinstance(chunk, dict): # Sometimes chunk is a MessageContent object
                             content = chunk.get("content", "")
                             if content: text_area.append(str(content))
                        elif isinstance(chunk, str): # Simpler case
                             if chunk: text_area.append(chunk)
                    elif inner_event_type == "on_tool_stream" and isinstance(inner_event_data, dict):
                        # LangGraph tool output stream
                        tool_chunk = inner_event_data.get("chunk", "")
                        if tool_chunk: # May need specific formatting for tool output
                            text_area.append(Text.from_markup(f"[italic yellow]Tool output: {tool_chunk}[/italic]\n"))
                    elif inner_event_type == "on_chain_end" or inner_event_type == "on_graph_end":
                        # End of a LangGraph chain/graph execution
                        # May contain final output not captured by token streams
                        # text_area.append(Text.from_markup("\n[grey50]Processing complete.[/grey50]"))
                        # Check inner_event_data for final messages if needed.
                        # For now, we assume most content comes via on_chat_model_stream.
                        # If the stream naturally ends after this, we might not need to break explicitly.
                        pass # Often, this is just a signal, actual content is streamed.
                    elif event_type == "stream_end" or event_type == "agent_response_end": # Hypothetical explicit end
                        text_area.append(Text.from_markup("\n[yellow]AI stream finished.[/yellow]"))
                        break
                    elif event_type == "error" or inner_event_type == "on_error":
                        error_content = inner_event_data.get("message", "Unknown error from server.")
                        if isinstance(inner_event_data, dict) and "error" in inner_event_data: # More specific error
                            error_content = str(inner_event_data.get("error", error_content))
                        text_area.append(Text.from_markup(f"\n[bold red]Server Error: {error_content}[/bold red]"))
                        break
                    # Add more specific event handling as discovered
                    # else:
                    #    text_area.append(Text.from_markup(f"\n[grey30]Received event: {event_type}, data: {event_data}[/grey30]"))

                    live_display.update(Panel(text_area, title="[bold green]AI[/bold green]", border_style="green", expand=False, subtitle="Streaming..."))

                except asyncio.TimeoutError:
                    text_area.append(Text.from_markup("\n[yellow]Timeout: No new data from server. Stream may have ended.[/yellow]"))
                    break
                except Exception as e:
                    self.console.print_exception(max_frames=4)
                    text_area.append(Text.from_markup(f"\n[bold red]Client error processing message: {type(e).__name__} - {e}[/bold red]"))
                    break

            # Final update to panel, remove subtitle
            live_display.update(Panel(text_area, title="[bold green]AI[/bold green]", border_style="green", expand=False, subtitle="Done."))

        except ConnectionRefusedError: # Specific error for connect()
             text_area.append(Text.from_markup(f"\n[bold red]Connection Refused: Could not connect to {self.server_url}. Ensure server is running.[/bold red]"))
        except Exception as e:
            self.console.print_exception(max_frames=4)
            text_area.append(Text.from_markup(f"\n[bold red]Failed to send/stream: {type(e).__name__} - {e}[/bold red]"))

        # Ensure the panel is updated one last time, especially if an error occurred early
        live_display.update(Panel(text_area, title="[bold green]AI[/bold green]", border_style="red" if "Error" in text_area.plain else "green", expand=False))


    async def chat_loop(self):
        self.console.print("[bold cyan]Rich Chat Client - Streaming Mode[/bold cyan]")
        self.console.print("Type 'exit' or press Ctrl+D to end the chat. Ctrl+C to interrupt.")

        if not await self.connect():
            return

        thread_id = f"cli-thread-{uuid.uuid4()}"
        self.console.print(f"Chat session started. Thread ID: [dim]{thread_id}[/dim]")

        try:
            while True:
                try:
                    user_input = await self.console.input_async(Text.from_markup(f"[bold blue]You ({thread_id[:8]}): [/bold blue]"))
                except EOFError:
                    self.console.print(Text.from_markup("\n[bold yellow]Exiting chat (Ctrl+D)...[/bold yellow]"))
                    break

                if user_input is None: # Should also be caught by EOFError
                    self.console.print(Text.from_markup("\n[bold yellow]Exiting chat (input stream closed)...[/bold yellow]"))
                    break

                if user_input.lower() == "exit":
                    self.console.print(Text.from_markup("\n[bold yellow]Exiting chat...[/bold yellow]"))
                    break

                if not user_input.strip():
                    continue

                self.console.print(Panel(Text(user_input, overflow="fold"), title=Text.from_markup(f"[bold blue]You ({thread_id[:8]})[/bold blue]"), title_align="left", border_style="blue", expand=False))

                ai_response_text_area = Text() # Reset for each new AI response
                ai_panel = Panel(ai_response_text_area, title=Text.from_markup("[bold green]AI[/bold green]"), title_align="left", border_style="green", expand=False)

                with Live(ai_panel, console=self.console, refresh_per_second=10, vertical_overflow="visible") as live:
                    await self.send_and_stream_response(user_input, thread_id, live, ai_response_text_area)

        except KeyboardInterrupt:
            self.console.print(Text.from_markup("\n[bold red]Chat interrupted by user (Ctrl+C).[/bold red]"))
        except Exception as e:
            self.console.print(Text.from_markup(f"[bold red]An unexpected error occurred in the chat loop: {e}[/bold red]"))
            self.console.print_exception(max_frames=4)
        finally:
            await self.disconnect()


async def main_test(): # Renamed to avoid conflict if this file is imported
    """For standalone testing of the RichCLIClient."""
    loop = asyncio.get_event_loop()
    # Ensure this URL matches your running MCP SSE server endpoint for chat
    # This is typically the /sse endpoint of the MCP server.
    client = RichCLIClient(server_url="http://localhost:8005/sse", loop=loop)
    await client.chat_loop()

if __name__ == "__main__":
    # This allows running this client directly for testing purposes.
    # The main CLI application will import RichCLIClient and use it differently.
    print("Running RichCLIClient standalone test...")
    try:
        asyncio.run(main_test())
    except KeyboardInterrupt:
        print("\nClient test terminated by user.")
    except Exception as e:
        print(f"Client test failed: {e}")
