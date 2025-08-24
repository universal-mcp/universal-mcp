from typing import Annotated, Any, Union, get_args, get_origin

from langchain_core.tools.base import (
    BaseTool,
    get_all_basemodel_annotations,
)
from langgraph.prebuilt import InjectedState, InjectedStore
from langgraph.store.base import BaseStore

ToolId = str


def get_default_retrieval_tool(
    namespace_prefix: tuple[str, ...],
    *,
    limit: int = 2,
    filter: dict[str, Any] | None = None,
):
    """Get default sync and async functions for tool retrieval."""

    def retrieve_tools(
        query: str,
        *,
        store: Annotated[BaseStore, InjectedStore],
    ) -> list[ToolId]:
        """Retrieve a tool to use, given a search query."""
        results = store.search(
            namespace_prefix,
            query=query,
            limit=limit,
            filter=filter,
        )
        return [result.key for result in results]

    async def aretrieve_tools(
        query: str,
        *,
        store: Annotated[BaseStore, InjectedStore],
    ) -> list[ToolId]:
        """Retrieve a tool to use, given a search query."""
        results = await store.asearch(
            namespace_prefix,
            query=query,
            limit=limit,
            filter=filter,
        )
        return [result.key for result in results]

    return retrieve_tools, aretrieve_tools


def _is_injection(type_arg: Any, injection_type: type[InjectedState] | type[InjectedStore]) -> bool:
    if isinstance(type_arg, injection_type) or (isinstance(type_arg, type) and issubclass(type_arg, injection_type)):
        return True
    origin_ = get_origin(type_arg)
    if origin_ is Union or origin_ is Annotated:
        return any(_is_injection(ta, injection_type) for ta in get_args(type_arg))
    return False


def get_store_arg(tool: BaseTool) -> str | None:
    full_schema = tool.get_input_schema()
    for name, type_ in get_all_basemodel_annotations(full_schema).items():
        injections = [type_arg for type_arg in get_args(type_) if _is_injection(type_arg, InjectedStore)]
        if len(injections) > 1:
            ValueError(
                "A tool argument should not be annotated with InjectedStore more than "
                f"once. Received arg {name} with annotations {injections}."
            )
        elif len(injections) == 1:
            return name
        else:
            pass

    return None
