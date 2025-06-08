# src/universal_mcp/client/chat_client.py
import asyncio
import uuid # For thread_id generation
from typing import Any, Dict, Union, Optional # Added Dict, Union, Optional

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
# from rich.json import JSON # For pretty printing dicts - not used in current snippet

# Agent base class for type hinting
from universal_mcp.agents.base import Agent
# No longer directly uses mcp.ClientSession or mcp.Message for agent comms
# from mcp import ClientSession, Message
# from mcp.client.sse import sse_client
# from universal_mcp.config import ClientTransportConfig, SSETransportConfig # Not needed anymore


class RichCLIClient:
    """
    A Rich-based CLI client for interacting with an Agent.
    This client handles the UI and user interaction loop.
    """
    def __init__(self, agent: Agent, loop: Optional[asyncio.AbstractEventLoop] = None): # loop is optional now
        """
        Initializes the RichCLIClient.

        Args:
            agent: An instance of an Agent (e.g., CLIAgent) that will handle
                   the conversation logic and communication with the language model.
            loop: The asyncio event loop. If None, asyncio.get_event_loop() will be used.
        """
        self.agent = agent
        self.loop = loop or asyncio.get_event_loop()
        self.console = Console()
        # Removed: self.server_url, self.session, self.exit_stack as they related to direct SSE connection

    # Removed connect() and disconnect() methods as session management for agent comms is now in the Agent.

    # Removed simulate_send_and_receive() and send_and_stream_response() methods
    # as their logic is now primarily within the Agent's stream_response().

    async def chat_loop(self):
        """
        Runs the main interactive chat loop.
        """
        self.console.print("[bold cyan]Rich CLI Chat Client[/bold cyan]")
        self.console.print("Type 'exit' or press Ctrl+D to end the chat.")
        self.console.print("Press Ctrl+C to interrupt and exit immediately.")

        # Thread ID can be generated per session or passed around
        thread_id = f"cli-thread-{str(uuid.uuid4())[:8]}"
        self.console.print(f"Chat session started. Thread ID: [dim]{thread_id}[/dim]")

        try:
            while True:
                try:
                    user_input = await self.console.input_async(Text.from_markup(f"[bold blue]You ({thread_id}): [/bold blue]"))
                except EOFError:  # Ctrl+D
                    self.console.print(Text.from_markup("\n[bold yellow]Exiting chat (Ctrl+D)...[/bold yellow]"))
                    break

                if user_input is None: # Should also be caught by EOFError
                    self.console.print(Text.from_markup("\n[bold yellow]Exiting chat (input stream closed)...[/bold yellow]"))
                    break

                if not user_input.strip(): # Skip empty input
                    continue

                if user_input.lower() == "exit":
                    self.console.print(Text.from_markup("\n[bold yellow]Exiting chat...[/bold yellow]"))
                    break

                # Display user's message using Rich Panel
                self.console.print(Panel(Text(user_input, overflow="fold"),
                                         title=Text.from_markup(f"[bold blue]You ({thread_id})[/bold blue]"),
                                         title_align="left", border_style="blue", expand=False))

                ai_response_text_area = Text()
                current_subtitle = "Streaming..."
                panel_border_style = "green" # Default for AI response

                # Pass http_session if agent needs it (e.g. CLIAgent for sse_client)
                # This is a bit of a workaround. Ideally, http_session management would be cleaner.
                # For now, we assume the agent might pick it from kwargs if needed.
                # http_session = getattr(self, '_http_session_for_agent', None) # Example if client managed a session

                with Live(Panel(ai_response_text_area,
                                title=Text.from_markup("[bold green]AI[/bold green]"),
                                subtitle=Text.from_markup(f"[italic grey50]{current_subtitle}[/italic grey50]"),
                                border_style=panel_border_style, expand=False),
                          console=self.console, refresh_per_second=12, vertical_overflow="visible") as live:

                    try:
                        # kwargs_for_agent = {}
                        # if http_session:
                        #     kwargs_for_agent["http_session"] = http_session

                        async for response_part in self.agent.stream_response(
                            user_message=user_input,
                            thread_id=thread_id
                            # **kwargs_for_agent # Pass any extra args agent might need
                            ):
                            if isinstance(response_part, str):
                                ai_response_text_area.append(response_part)
                            elif isinstance(response_part, dict):
                                event_type = response_part.get("type", "unknown_event")
                                event_data = response_part.get("data", {})

                                if event_type == "error":
                                    error_content = event_data.get('content', 'Unknown error from agent.')
                                    ai_response_text_area.append(Text.from_markup(f"\n[bold red]Agent Error: {error_content}[/bold red]"))
                                    current_subtitle = "Error"
                                    panel_border_style = "red"
                                    # No break here, allow agent to yield more if it wants, or UI to show final state
                                elif event_type == "info":
                                    info_content = event_data.get('status', event_data.get('content', str(event_data)))
                                    ai_response_text_area.append(Text.from_markup(f"\n[italic yellow]Info: {info_content}[/italic yellow]"))
                                elif event_type == "tool_event" and isinstance(event_data, dict): # From CLIAgent
                                    event_name = response_part.get("event_name", "unknown_tool_event")
                                    tool_data = response_part.get("data", {})
                                    tool_name = tool_data.get('name', 'Unknown tool')
                                    if event_name == "on_tool_start":
                                        tool_input = tool_data.get('input', {})
                                        ai_response_text_area.append(Text.from_markup(f"\n[italic magenta]Tool Start: {tool_name} (Input: {str(tool_input)[:50]}...)[/italic magenta]"))
                                    elif event_name == "on_tool_end":
                                        tool_output = str(tool_data.get('output', 'No output'))
                                        ai_response_text_area.append(Text.from_markup(f"\n[italic magenta]Tool End: {tool_name} (Output: {tool_output[:100]}...)[/italic magenta]"))
                                    else: # on_tool_stream or other tool events
                                        ai_response_text_area.append(Text.from_markup(f"\n[italic magenta]Tool Event ({event_name}): {str(tool_data)[:100]}...[/italic magenta]"))
                                elif event_type == "structured_message" and isinstance(event_data, dict):
                                    # For other fully structured messages from agent
                                    summary = str(event_data)[:100]
                                    ai_response_text_area.append(Text.from_markup(f"\n[dim]Structured: {summary}... [/dim]"))
                                    # Could use rich.json.JSON(event_data) here if desired
                                else:
                                    summary = str(response_part)[:100]
                                    ai_response_text_area.append(Text.from_markup(f"\n[grey50]Received data: {summary}...[/grey50]"))
                            else:
                                ai_response_text_area.append(Text.from_markup(f"\n[grey50]Received (unknown type): {str(response_part)}[/grey50]"))

                            live.update(Panel(ai_response_text_area,
                                        title=Text.from_markup("[bold green]AI[/bold green]"),
                                        subtitle=Text.from_markup(f"[italic grey50]{current_subtitle}[/italic grey50]"),
                                        border_style=panel_border_style, expand=False))

                        if current_subtitle == "Streaming...": # If loop finished without error/specific end
                            current_subtitle = "Done"

                    except Exception as e:
                        # self.console.print_exception(show_locals=True) # For debugging
                        error_msg = Text.from_markup(f"\n[bold red]Client error during agent stream: {type(e).__name__} - {e}[/bold red]")
                        ai_response_text_area.append(error_msg)
                        current_subtitle = "Client Error"
                        panel_border_style = "red"
                    finally:
                        live.update(Panel(ai_response_text_area,
                                    title=Text.from_markup("[bold green]AI[/bold green]"),
                                    subtitle=Text.from_markup(f"[italic grey50]{current_subtitle}[/italic grey50]"),
                                    border_style=panel_border_style, expand=False))

        except KeyboardInterrupt:
            self.console.print(Text.from_markup("\n[bold red]Chat interrupted by user (Ctrl+C).[/bold red]"))
        except Exception as e:
            self.console.print(Text.from_markup(f"[bold red]An critical error occurred in the chat client: {e}[/bold red]"))
            self.console.print_exception(max_frames=4) # For debugging critical client errors
        # No finally block for self.disconnect() as it's removed.

# Standalone testing part is removed as RichCLIClient now depends on an Agent instance.
# async def main_test():
#     pass # Would need a mock agent

# if __name__ == "__main__":
#     # asyncio.run(main_test())
#     pass
