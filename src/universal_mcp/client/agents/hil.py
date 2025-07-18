from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Interrupt, interrupt

from universal_mcp.client.agents.base import BaseAgent
from universal_mcp.client.agents.llm import get_llm


class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str | None = None
    favourite_color: str | None = None
    human: bool | None = None


def ask_name_node(state: State) -> State:
    if state.get("name") is not None:
        return state
    name = interrupt({"question": "What is your name?", "type": "text"})
    state.update(name=name, messages=[HumanMessage(content=f"My name is {name}")])
    return state


def ask_bool_node(state: State) -> State:
    if state.get("human") is not None:
        return state
    bool = interrupt({"question": "Are you a human?", "type": "bool"})

    if bool:
        state.update(human=True, messages=[HumanMessage(content="I am human")])
    else:
        state.update(human=False, messages=[HumanMessage(content="I am AI agent")])
    return state


def ask_favourite_color_node(state: State) -> State:
    if state.get("favourite_color") is not None:
        return state
    favourite_color = interrupt(
        {"question": "What is your favourite color?", "type": "choice", "choices": ["red", "green", "blue"]}
    )
    state.update(
        favourite_color=favourite_color, messages=[HumanMessage(content=f"My favourite color is {favourite_color}")]
    )
    return state


def handle_interrupt(interrupt: Interrupt) -> str | bool:
    interrupt_type = interrupt.value["type"]
    if interrupt_type == "text":
        value = input(interrupt.value["question"])
        return value
    elif interrupt_type == "bool":
        value = input("Do you accept this? (y/n): " + interrupt.value["question"])
        return value.lower() in ["y", "yes"]
    elif interrupt_type == "choice":
        value = input("Enter your choice: " + interrupt.value["question"] + " " + ", ".join(interrupt.value["choices"]))
        if value in interrupt.value["choices"]:
            return value
        else:
            return interrupt.value["choices"][0]
    else:
        raise ValueError(f"Invalid interrupt type: {interrupt.value['type']}")


class HilAgent(BaseAgent):
    def __init__(self, name: str, instructions: str, model: str):
        super().__init__(name, instructions, model)
        self.llm = get_llm(model)
        self._graph = self._build_graph()

    def chatbot(self, state: State):
        return {"messages": [self.llm.invoke(state["messages"])]}

    def _build_graph(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("ask_name_node", ask_name_node)
        graph_builder.add_node("ask_bool_node", ask_bool_node)
        graph_builder.add_node("ask_favourite_color_node", ask_favourite_color_node)
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_edge(START, "ask_name_node")
        graph_builder.add_edge("ask_name_node", "ask_bool_node")
        graph_builder.add_edge("ask_bool_node", "ask_favourite_color_node")
        graph_builder.add_edge("ask_favourite_color_node", "chatbot")
        graph_builder.add_edge("chatbot", END)
        return graph_builder.compile(checkpointer=self.memory)

    @property
    def graph(self):
        return self._graph


if __name__ == "__main__":
    import asyncio

    agent = HilAgent(
        "Hil Agent", "You are a friendly agent that asks for the user's name and greets them.", "openrouter/auto"
    )
    # graph = agent.graph
    # config = {"configurable": {"thread_id": uuid.uuid4()}}
    # while True:
    #     state = agent.graph.get_state(config=config)
    #     if state.interrupts:
    #         value = handle_interrupt(state.interrupts[0])
    #         result = graph.invoke(Command(resume=value), config=config)
    #     else:
    #         user_input = input("You: ")
    #         result = graph.invoke({"messages": [{"role": "user", "content": user_input}]}, config=config)
    #     interrupts = result.get("__interrupt__")
    #     if not interrupts:
    #         to_print = result.get("messages")[-1].content
    #         print(to_print)

    asyncio.run(agent.run_interactive())
