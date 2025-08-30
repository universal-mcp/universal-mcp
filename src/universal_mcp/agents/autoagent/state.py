from typing import Annotated

from langgraph.prebuilt.chat_agent_executor import AgentState


def _enqueue(left: list, right: list) -> list:
    """Treat left as a FIFO queue, append new items from right (preserve order),
    keep items unique, and cap total size to 20 (drop oldest items)."""
    max_size = 30
    preferred_size = 20
    if len(right) > preferred_size:
        preferred_size = min(max_size, len(right))
    queue = list(left or [])

    for item in right[:preferred_size] or []:
        if item in queue:
            queue.remove(item)
        queue.append(item)

    if len(queue) > preferred_size:
        queue = queue[-preferred_size:]

    return queue


class State(AgentState):
    selected_tool_ids: Annotated[list[str], _enqueue]
