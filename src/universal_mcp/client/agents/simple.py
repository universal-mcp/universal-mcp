import asyncio
from typing import Annotated

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from universal_mcp.client.agents.base import BaseAgent
from universal_mcp.client.agents.llm import get_llm


class State(TypedDict):
    messages: Annotated[list, add_messages]


class SimpleAgent(BaseAgent):
    def __init__(self, name: str, instructions: str, model: str):
        super().__init__(name, instructions, model)
        self.llm = get_llm(model)
        self._graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(State)

        def chatbot(state: State):
            return {"messages": [self.llm.invoke(state["messages"])]}

        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        return graph_builder.compile(checkpointer=self.memory)

    @property
    def graph(self):
        return self._graph


if __name__ == "__main__":
    agent = SimpleAgent("Simple Agent", "You are a helpful assistant", "openrouter/auto")
    asyncio.run(agent.run_interactive())
