import asyncio

from langgraph.checkpoint.base import BaseCheckpointSaver

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.planner.graph import graph_builder
from universal_mcp.agents.react import ReactAgent
from universal_mcp.tools.registry import ToolRegistry


class PlannerAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        registry: ToolRegistry,
        memory: BaseCheckpointSaver | None = None,
        executor_agent_cls: type[BaseAgent] = ReactAgent,
        **kwargs,
    ):
        super().__init__(name, instructions, model, memory, **kwargs)
        self.app_registry = registry
        self.llm = load_chat_model(model)
        self.executor_agent_cls = executor_agent_cls

    async def _build_graph(self):
        return graph_builder(
            self.llm, self.app_registry, self.instructions, self.model, self.executor_agent_cls
        ).compile(checkpointer=self.memory)

    @property
    def graph(self):
        return self._graph


async def main():
    from universal_mcp.agentr.registry import AgentrRegistry

    registry = AgentrRegistry()
    agent = PlannerAgent(
        name="planner-agent",
        instructions="You are a helpful assistant.",
        model="gemini/gemini-2.5-flash",
        registry=registry,
    )
    from rich.console import Console

    console = Console()
    console.print("Starting agent...", style="yellow")
    async for event in agent.stream(user_input="Send an email to manoj@agentr.dev'", thread_id="xyz"):
        console.print(event.content, style="red")


if __name__ == "__main__":
    asyncio.run(main())
