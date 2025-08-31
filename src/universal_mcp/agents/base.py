# agents/base.py
from typing import cast
from uuid import uuid4

from langchain_core.messages import AIMessageChunk
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from .utils import RichCLI


class BaseAgent:
    def __init__(self, name: str, instructions: str, model: str, memory: BaseCheckpointSaver | None = None, **kwargs):
        self.name = name
        self.instructions = instructions
        self.model = model
        self.memory = memory or MemorySaver()
        self._graph = None
        self._initialized = False
        self.cli = RichCLI()

    async def ainit(self):
        if not self._initialized:
            self._graph = await self._build_graph()
            self._initialized = True

    async def _build_graph(self):
        raise NotImplementedError("Subclasses must implement this method")

    async def stream(self, thread_id: str, user_input: str):
        await self.ainit()
        async for event, metadata in self._graph.astream(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"configurable": {"thread_id": thread_id}},
            context={"system_prompt": self.instructions, "model": self.model},
            stream_mode="messages",
            stream_usage=True,
        ):
            # Only forward assistant token chunks that are not tool-related.
            event = cast(AIMessageChunk, event)
            if "finish_reason" in event.response_metadata:
                # Got LLM finish reason ignore it
                # logger.debug(f"Finish event: {event}")
                continue

            # Skip chunks that correspond to tool calls or tool execution phases
            # - tool_call_chunks present => model is emitting tool call(s)
            # - metadata tags or node names may indicate tool/quiet phases
            tags = metadata.get("tags", []) if isinstance(metadata, dict) else []

            is_quiet = isinstance(tags, list) and ("quiet" in tags)

            if is_quiet:
                continue

            # Emit only the token chunks for the final assistant message.
            # logger.debug(f"Event: {event}, Metadata: {metadata}")
            yield event
        # Send a final finished message
        # The last event would be finish
        event = cast(AIMessageChunk, event)
        yield event

    async def stream_interactive(self, thread_id: str, user_input: str):
        await self.ainit()
        with self.cli.display_agent_response_streaming(self.name) as stream_updater:
            async for event in self.stream(thread_id, user_input):
                stream_updater.update(event.content)

    async def invoke(self, user_input: str, thread_id: str = str(uuid4())):
        """Run the agent"""
        await self.ainit()
        return await self._graph.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"configurable": {"thread_id": thread_id}},
            context={"system_prompt": self.instructions, "model": self.model},
        )

    async def run_interactive(self, thread_id: str = str(uuid4())):
        """Main application loop"""

        await self.ainit()
        # Display welcome
        self.cli.display_welcome(self.name)

        # Main loop
        while True:
            try:
                state = self._graph.get_state(config={"configurable": {"thread_id": thread_id}})
                if state.interrupts:
                    value = self.cli.handle_interrupt(state.interrupts[0])
                    self._graph.invoke(Command(resume=value), config={"configurable": {"thread_id": thread_id}})
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
                import traceback

                traceback.print_exc()
                self.cli.display_error(f"An error occurred: {str(e)}")
