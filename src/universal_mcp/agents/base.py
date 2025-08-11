# agents/base.py
from typing import cast
from uuid import uuid4

from langchain_core.messages import AIMessageChunk
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from .utils import RichCLI


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

    async def stream(self, thread_id: str, user_input: str):
        async for event, _ in self.graph.astream(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"configurable": {"thread_id": thread_id}},
            stream_mode="messages",
        ):
            event = cast(AIMessageChunk, event)
            yield event

    async def stream_interactive(self, thread_id: str, user_input: str):
        with self.cli.display_agent_response_streaming(self.name) as stream_updater:
            async for event in self.stream(thread_id, user_input):
                stream_updater.update(event.content)

    async def process_command(self, command: str) -> bool | None:
        """Process a command from the user"""

    async def run_interactive(self, thread_id: str = str(uuid4())):
        """Main application loop"""

        # Display welcome
        self.cli.display_welcome(self.name)

        # Main loop
        while True:
            try:
                state = self.graph.get_state(config={"configurable": {"thread_id": thread_id}})
                if state.interrupts:
                    value = self.cli.handle_interrupt(state.interrupts[0])
                    self.graph.invoke(Command(resume=value), config={"configurable": {"thread_id": thread_id}})
                    continue

                user_input = self.cli.get_user_input()
                if not user_input.strip():
                    continue

                # Process commands
                if user_input.startswith("/"):
                    command = user_input.lower().lstrip("/")
                    if command == "about":
                        self.cli.display_info(f"Agent is {self.name}. {self.instructions}")
                        continue
                    elif command == "exit" or command == "quit" or command == "q":
                        self.cli.display_info("Goodbye! 👋")
                        break
                    elif command == "reset":
                        self.cli.clear_screen()
                        self.cli.display_info("Resetting agent...")
                        thread_id = str(uuid4())
                        continue
                    elif command == "help":
                        self.cli.display_info("Available commands: /about, /exit, /quit, /q, /reset")
                        continue
                    else:
                        self.cli.display_error(f"Unknown command: {command}")
                        continue

                # Process with agent
                await self.stream_interactive(thread_id, user_input)

            except KeyboardInterrupt:
                self.cli.display_info("\nGoodbye! 👋")
                break
            except Exception as e:
                self.cli.display_error(f"An error occurred: {str(e)}")
