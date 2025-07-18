import uuid
from typing import Annotated, TypedDict

from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, Interrupt, interrupt

from universal_mcp.client.agents.base import BaseAgent
from universal_mcp.client.agents.llm import get_llm


class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str = ""
    favourite_color: str = ""
    greeting: str = ""


def ask_name_node(state: State) -> State:
    name = interrupt({"question": "What is your name?", "type": "text"})
    state.update(name=name)
    return state


def ask_bool_node(state: State) -> State:
    bool = interrupt({"question": "Are you a human?", "type": "bool"})
    if bool:
        return {"name": state["name"], "greeting": "Hello, human!"}
    else:
        return {"name": state["name"], "greeting": "Hello, non-human!"}


def ask_favourite_color_node(state: State) -> State:
    favourite_color = interrupt(
        {"question": "What is your favourite color?", "type": "choice", "choices": ["red", "green", "blue"]}
    )
    state.update(favourite_color=favourite_color)
    return state


def greeting_node(state: State) -> State:
    greeting = f"Greeting {state['name']}! {state['greeting']} Your favourite color is {state['favourite_color']}"
    state.update(greeting=greeting)
    return state


# Pass a thread ID to the graph to run it.
config = {"configurable": {"thread_id": uuid.uuid4()}}

# Run the graph until the interrupt is hit.


def handle_interrupt(interrupt: Interrupt) -> str | bool:
    interrupt_type = interrupt.value["type"]
    if interrupt_type == "text":
        value = input(interrupt.value["question"])
        return value
    elif interrupt_type == "bool":
        value = input(interrupt.value["question"])
        return value.lower() in ["y", "yes"]
    elif interrupt_type == "choice":
        value = input(interrupt.value["question"] + " " + ", ".join(interrupt.value["choices"]))
        if value in interrupt.value["choices"]:
            return value
        else:
            return interrupt.value["choices"][0]
    else:
        raise ValueError(f"Invalid interrupt type: {interrupt.value['type']}")


def ask_for_input(state: State, query: str) -> str:
    """Interrupts the agent to ask the user for input."""
    response = input(query)
    return response


def ask_for_confirmation(state: State, query: str) -> bool:
    """Interrupts the agent to ask the user for yes/no confirmation."""
    response = input(f"{query} (y/n): ").strip().lower()
    return response == "y"


def ask_for_choice(state: State, query: str, options: list[str]) -> str:
    """Interrupts the agent to ask the user to choose from options."""
    print(f"{query} Options: {', '.join(options)}")
    response = input("Your choice: ").strip()
    if response in options:
        return response
    return None


class HilAgent(BaseAgent):
    def __init__(self, name: str, instructions: str, model: str):
        super().__init__(name, instructions, model)
        self.llm = get_llm(model)
        self._graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("ask_name_node", ask_name_node)
        graph_builder.add_node("ask_bool_node", ask_bool_node)
        graph_builder.add_node("ask_favourite_color_node", ask_favourite_color_node)
        graph_builder.add_node("greeting_node", greeting_node)
        graph_builder.add_edge(START, "ask_name_node")
        graph_builder.add_edge("ask_name_node", "ask_bool_node")
        graph_builder.add_edge("ask_bool_node", "ask_favourite_color_node")
        graph_builder.add_edge("ask_favourite_color_node", "greeting_node")
        graph_builder.add_edge("greeting_node", END)
        return graph_builder.compile(checkpointer=self.memory)

    @property
    def graph(self):
        return self._graph


if __name__ == "__main__":
    agent = HilAgent(
        "Hil Agent", "You are a friendly agent that asks for the user's name and greets them.", "openrouter/auto"
    )
    graph = agent.graph
    result = None
    result = graph.invoke({"name": "", "greeting": "", "favourite_color": ""}, config=config)
    print(result)
    i1 = result.get("__interrupt__")[0]
    name = handle_interrupt(i1)
    result = graph.invoke(Command(resume=name), config=config)
    print(result)
    i2 = result.get("__interrupt__")[0]
    bool = handle_interrupt(i2)
    result = graph.invoke(Command(resume=bool), config=config)
    print(result)
    i3 = result.get("__interrupt__")[0]
    favourite_color = handle_interrupt(i3)
    result = graph.invoke(Command(resume=favourite_color), config=config)
    print(result)

    # asyncio.run(agent.run_interactive())
