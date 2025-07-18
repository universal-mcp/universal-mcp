import json
from contextlib import contextmanager

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


class RichCLI:
    def __init__(self):
        self.console = Console()

    def display_welcome(self, agent_name: str):
        """Display welcome message"""
        welcome_text = f"""
# Welcome to {agent_name}!

Available commands:
- Type your questions naturally
- `/help` - Show help
- `/tools` - List available tools
- `/exit` - Exit the application
        """
        self.console.print(Panel(Markdown(welcome_text), title="🤖 AI Agent CLI", border_style="blue"))

    def display_agent_response(self, response: str, agent_name: str):
        """Display agent response with formatting"""
        self.console.print(Panel(Markdown(response), title=f"🤖 {agent_name}", border_style="green", padding=(1, 2)))

    @contextmanager
    def display_agent_response_streaming(self, agent_name: str):
        """Context manager for streaming agent response updates."""

        with Live(refresh_per_second=10, console=self.console) as live:

            class StreamUpdater:
                content = []

                def update(self, chunk: str):
                    self.content.append(chunk)
                    panel = Panel(
                        Markdown("".join(self.content)),
                        title=f"🤖 {agent_name}",
                        border_style="green",
                        padding=(1, 2),
                    )
                    live.update(panel)

            yield StreamUpdater()

    def display_thinking(self, thought: str):
        """Display agent's thinking process"""
        if thought:
            self.console.print(Panel(thought, title="💭 Thinking", border_style="yellow", padding=(1, 2)))

    def display_tools(self, tools: list):
        """Display available tools in a table"""
        table = Table(title="🛠️ Available Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Description", style="white")

        for tool in tools:
            func_info = tool["function"]
            table.add_row(func_info["name"], func_info["description"])

        self.console.print(table)

    def display_tool_call(self, tool_call: dict):
        """Display tool call"""
        tool_call_str = json.dumps(tool_call, indent=2)
        self.console.print(Panel(tool_call_str, title="🛠️ Tool Call", border_style="green", padding=(1, 2)))

    def display_tool_result(self, tool_result: dict):
        """Display tool result"""
        tool_result_str = json.dumps(tool_result, indent=2)
        self.console.print(Panel(tool_result_str, title="🛠️ Tool Result", border_style="green", padding=(1, 2)))

    def display_error(self, error: str):
        """Display error message"""
        self.console.print(Panel(error, title="❌ Error", border_style="red"))

    def get_user_input(self) -> str:
        """Get user input with rich prompt"""
        return Prompt.ask("[bold blue]You[/bold blue]", console=self.console)

    def display_info(self, message: str):
        """Display info message"""
        self.console.print(f"[bold cyan]ℹ️ {message}[/bold cyan]")

    def clear_screen(self):
        """Clear the screen"""
        self.console.clear()
