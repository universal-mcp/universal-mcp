from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from universal_mcp.applications.sample_tool_app import SampleToolApp
from universal_mcp.client.agents import AgentType, ReActAgent
from universal_mcp.tools.adapters import ToolFormat
from universal_mcp.tools.manager import ToolManager


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
- `/switch <agent_type>` - Switch agent type (react/codeact)
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

    def display_error(self, error: str):
        """Display error message"""
        self.console.print(Panel(error, title="❌ Error", border_style="red"))

    def get_user_input(self) -> str:
        """Get user input with rich prompt"""
        return Prompt.ask("[bold blue]You[/bold blue]", console=self.console)

    def display_info(self, message: str):
        """Display info message"""
        self.console.print(f"[bold cyan]ℹ️ {message}[/bold cyan]")


class AgentCLI:
    def __init__(self):
        self.cli = RichCLI()
        self.tool_manager = ToolManager(default_format=ToolFormat.OPENAI)
        self.current_agent = None
        self.agent_type = AgentType.REACT
        self.tool_manager.register_tools_from_app(SampleToolApp(), tags=["all"])

    def create_agent(self, agent_type: AgentType, model: str = "gpt-4o") -> Any:
        """Create an agent based on type"""
        instructions = """You are a helpful AI assistant. Use the available tools to help users with their requests.
        Think step by step and provide clear explanations of your reasoning."""

        if agent_type == AgentType.REACT:
            return ReActAgent("ReAct Agent", instructions, model)
        else:
            raise ValueError("Unknown agent type")

    def switch_agent(self, agent_type: str):
        """Switch to a different agent type"""
        try:
            self.agent_type = AgentType(agent_type.lower())
            self.current_agent = self.create_agent(self.agent_type)
            self.cli.display_info(f"Switched to {self.agent_type.value} agent")
        except ValueError:
            self.cli.display_error(f"Unknown agent type: {agent_type}")

    async def process_command(self, user_input: str) -> bool:
        """Process special commands, return True if command was processed"""
        if user_input.startswith("/"):
            command_parts = user_input[1:].split()
            command = command_parts[0].lower()

            if command == "help":
                self.show_help()
                return True
            elif command == "tools":
                self.cli.display_tools(self.tool_manager.list_tools())
                return True
            elif command == "switch" and len(command_parts) > 1:
                self.switch_agent(command_parts[1])
                return True
            elif command == "exit":
                self.cli.display_info("Goodbye! 👋")
                return False
            else:
                self.cli.display_error(f"Unknown command: {command}")
                return True

        return None  # Not a command

    def show_help(self):
        """Show help information"""
        help_text = """
# Available Commands

- `/help` - Show this help message
- `/tools` - List all available tools
- `/switch <type>` - Switch agent types:
  - `react` - ReAct reasoning agent
  - `codeact` - Code execution agent
- `/exit` - Exit the application

# Agent Types

**ReAct Agent**: Uses reasoning, action, observation loops

# Example Usage

- "What time is it?"
- "Calculate 15 * 7 + 23"
- "Search for information about Python"
        """
        self.cli.console.print(help_text)

    async def run(self, model: str = "gpt-4o-mini"):
        """Main application loop"""

        # Initialize agent
        self.current_agent = self.create_agent(self.agent_type, model)

        # Display welcome
        self.cli.display_welcome(self.current_agent.name)

        # Main loop
        while True:
            try:
                user_input = self.cli.get_user_input()

                if not user_input.strip():
                    continue

                # Process commands
                command_result = await self.process_command(user_input)
                if command_result is False:  # Exit command
                    break
                elif command_result is True:  # Command processed
                    continue

                # Process with agent
                response = await self.current_agent.process_step(user_input, self.tool_manager)

                self.cli.display_agent_response(response, self.current_agent.name)

            except KeyboardInterrupt:
                self.cli.display_info("\nGoodbye! 👋")
                break
            except Exception as e:
                self.cli.display_error(f"An error occurred: {str(e)}")
