import uuid
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.types import Command, Interrupt, interrupt


class State(TypedDict):
    # messages: Annotated[list, add_messages]
    name: str
    favourite_color: str
    greeting: str


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


def ask_form_node(state: State) -> State:
    form = interrupt({"question": "What is your name?", "type": "form", "fields": [{"name": "name", "type": "text"}]})
    print(form)
    state.update(form=form)
    return state


def greeting_node(state: State) -> State:
    greeting = f"Greeting {state['name']}! {state['greeting']} Your favourite color is {state['favourite_color']}"
    state.update(greeting=greeting)
    return state


# Build the graph
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

checkpointer = InMemorySaver()

graph = graph_builder.compile(checkpointer=checkpointer)

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


result = None
result = graph.invoke({"name": "", "greeting": "", "favourite_color": ""}, config=config)
i1 = result.get("__interrupt__")[0]
name = handle_interrupt(i1)
result = graph.invoke(Command(resume=name), config=config)
i2 = result.get("__interrupt__")[0]
bool = handle_interrupt(i2)
result = graph.invoke(Command(resume=bool), config=config)
i3 = result.get("__interrupt__")[0]
favourite_color = handle_interrupt(i3)
result = graph.invoke(Command(resume=favourite_color), config=config)
print(result)
