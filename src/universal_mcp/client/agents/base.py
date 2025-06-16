# agents/base.py
import json
from abc import ABC, abstractmethod

from rich.console import Console
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


class BaseAgent(ABC):
    def __init__(self, name: str, instructions: str, model: str):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.cli = RichCLI()

    @abstractmethod
    async def execute(self, user_input: str):
        """Execute the agent's logic."""
        raise NotImplementedError("Subclasses must implement this method")

    async def process_command(self, command: str) -> bool | None:
        """Process a command from the user"""
        command = command.lower().lstrip("/")
        if command == "about":
            self.cli.display_info(f"Agent is {self.name}. {self.instructions}")
            return True
        elif command == "exit" or command == "quit" or command == "q":
            self.cli.display_info("Goodbye! 👋")
            return False
        return True

    async def run_interactive(self):
        """Main application loop"""

        # Display welcome
        self.cli.display_welcome(self.name)

        # Main loop
        while True:
            try:
                user_input = self.cli.get_user_input()

                if not user_input.strip():
                    continue

                # Process commands
                if user_input.startswith("/"):
                    command_result = await self.process_command(user_input)
                    if command_result is False:  # Exit command
                        break
                    elif command_result is True:  # Command processed
                        continue

                # Process with agent
                response = await self.execute(user_input)

                self.cli.display_agent_response(response, self.name)

            except KeyboardInterrupt:
                self.cli.display_info("\nGoodbye! 👋")
                break
            except Exception as e:
                self.cli.display_error(f"An error occurred: {str(e)}")
