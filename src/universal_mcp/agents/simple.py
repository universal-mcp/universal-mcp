import asyncio
from typing import Annotated

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.llm import load_chat_model


class State(TypedDict):
    messages: Annotated[list, add_messages]


class SimpleAgent(BaseAgent):
    def __init__(self, name: str, instructions: str, model: str, memory: BaseCheckpointSaver = None, **kwargs):
        super().__init__(name, instructions, model, memory, **kwargs)
        self.llm = load_chat_model(model)

    async def _build_graph(self):
        graph_builder = StateGraph(State)

        async def chatbot(state: State):
            messages = [
                {"role": "system", "content": self.instructions},
                *state["messages"],
            ]
            return {"messages": [await self.llm.ainvoke(messages)]}

        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        return graph_builder.compile(checkpointer=self.memory)


if __name__ == "__main__":
    agent = SimpleAgent("Simple Agent", "You are a helpful assistant", "azure/gpt-4o")
    asyncio.run(agent.run_interactive())
