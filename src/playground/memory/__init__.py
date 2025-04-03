from langgraph.checkpoint.base import BaseCheckpointSaver

from playground.memory.sqlite import get_sqlite_saver


def initialize_database() -> BaseCheckpointSaver:
    """
    Initialize the appropriate database checkpointer based on configuration.
    Returns an initialized AsyncCheckpointer instance.
    """
    return get_sqlite_saver()


__all__ = ["initialize_database"]
