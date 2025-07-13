# agents/base.py
from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver

from universal_mcp.client.agents.cli import RichCLI


class BaseAgent:
    def __init__(self, name: str, instructions: str, model: str):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.memory = MemorySaver()
        self.cli = RichCLI()

    @property
    def graph(self):
        raise NotImplementedError("Subclasses must implement this method")

    async def stream_graph_updates(self, thread_id: str, user_input: str):
        with self.cli.display_agent_response_streaming(self.name) as stream_updater:
            async for token, _ in self.graph.astream(
                {"messages": [{"role": "user", "content": user_input}]},
                config={"configurable": {"thread_id": thread_id}},
                stream_mode="messages",
            ):
                stream_updater.update(token.content)

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

    async def run_interactive(self, thread_id: str = uuid4()):
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
                await self.stream_graph_updates(thread_id, user_input)

            except KeyboardInterrupt:
                self.cli.display_info("\nGoodbye! 👋")
                break
            except Exception as e:
                self.cli.display_error(f"An error occurred: {str(e)}")
