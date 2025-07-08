import asyncio
import json
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from playground.agents.react import create_agent
from playground.agents.auto_agent import create_auto_agent
from playground.schema import (
    ChatHistory,
    ChatMessage,
)
from playground.utils import (
    convert_message_content_to_string,
    langchain_to_chat_message,
    remove_tool_calls,
)


@asynccontextmanager
async def create_agent_client(agent_type: str = "auto"):
    """Create an agent client with the specified agent type."""
    if agent_type == "auto":
        async with create_auto_agent() as auto_agent:
            client = AutoAgentClient(auto_agent=auto_agent)
            yield client
    else:
        async with create_agent() as react_agent:
            agent = react_agent
            client = AgentClient(agent=agent)
            yield client


class AgentClientError(Exception):
    pass


class AgentClient:
    """Client for interacting with the agent directly."""

    def __init__(self, agent) -> None:
        """
        Initialize the client.

        Args:
            agent (Agent): The agent to use.
        """
        self.agent = agent

    def retrieve_info(self) -> None:
        """Get information about the agent."""
        # This is a placeholder method that doesn't need to do anything
        # since we're directly using the agent
        pass

    async def ainvoke(
        self,
        message: str,
        thread_id: str | None = None,
        agent_config: dict[str, Any] | None = None,
    ) -> ChatMessage:
        """
        Invoke the agent asynchronously. Only the final message is returned.

        Args:
            message (str): The message to send to the agent
            thread_id (str, optional): Thread ID for continuing a conversation
            agent_config (dict[str, Any], optional): Additional configuration to pass through to the agent

        Returns:
            ChatMessage: The response from the agent
        """
        run_id = uuid4()
        thread_id = thread_id or str(uuid4())

        configurable = {"thread_id": thread_id}
        if agent_config:
            if overlap := configurable.keys() & agent_config.keys():
                raise AgentClientError(f"agent_config contains reserved keys: {overlap}")
            configurable.update(agent_config)

        kwargs = {
            "input": {"messages": [HumanMessage(content=message)]},
            "config": RunnableConfig(
                configurable=configurable,
                run_id=run_id,
            ),
        }

        try:
            response = await self.agent.ainvoke(**kwargs)
            output = langchain_to_chat_message(response["messages"][-1])
            output.run_id = str(run_id)
            return output
        except Exception as e:
            raise AgentClientError(f"Error invoking agent: {e}") from e

    def invoke(
        self,
        message: str,
        thread_id: str | None = None,
        agent_config: dict[str, Any] | None = None,
    ) -> ChatMessage:
        """
        Invoke the agent synchronously. Only the final message is returned.

        Args:
            message (str): The message to send to the agent
            thread_id (str, optional): Thread ID for continuing a conversation
            agent_config (dict[str, Any], optional): Additional configuration to pass through to the agent

        Returns:
            ChatMessage: The response from the agent
        """
        run_id = uuid4()
        thread_id = thread_id or str(uuid4())

        configurable = {"thread_id": thread_id}
        if agent_config:
            if overlap := configurable.keys() & agent_config.keys():
                raise AgentClientError(f"agent_config contains reserved keys: {overlap}")
            configurable.update(agent_config)

        kwargs = {
            "input": {"messages": [HumanMessage(content=message)]},
            "config": RunnableConfig(
                configurable=configurable,
                run_id=run_id,
            ),
        }

        try:
            response = self.agent.invoke(**kwargs)
            output = langchain_to_chat_message(response["messages"][-1])
            output.run_id = str(run_id)
            return output
        except Exception as e:
            raise AgentClientError(f"Error invoking agent: {e}") from e

    def _parse_stream_line(self, line: str) -> ChatMessage | str | None:
        """
        Parse a line from the stream.

        This method is kept for compatibility but is no longer used
        since we're directly streaming from the agent.
        """
        line = line.strip()
        if line.startswith("data: "):
            data = line[6:]
            if data == "[DONE]":
                return None
            try:
                parsed = json.loads(data)
            except Exception as e:
                raise Exception(f"Error JSON parsing message: {e}") from e
            match parsed["type"]:
                case "message":
                    try:
                        return ChatMessage.model_validate(parsed["content"])
                    except Exception as e:
                        raise Exception(f"Invalid message format: {e}") from e
                case "token":
                    return parsed["content"]
                case "error":
                    raise Exception(parsed["content"])
        return None

    def stream(
        self,
        message: str,
        thread_id: str | None = None,
        agent_config: dict[str, Any] | None = None,
        stream_tokens: bool = True,
    ) -> Generator[ChatMessage | str, None, None]:
        """
        Stream the agent's response synchronously.

        Each intermediate message of the agent process is yielded as a ChatMessage.
        If stream_tokens is True (the default value), the response will also yield
        content tokens from streaming models as they are generated.

        Args:
            message (str): The message to send to the agent
            thread_id (str, optional): Thread ID for continuing a conversation
            agent_config (dict[str, Any], optional): Additional configuration to pass through to the agent
            stream_tokens (bool, optional): Stream tokens as they are generated
                Default: True

        Returns:
            Generator[ChatMessage | str, None, None]: The response from the agent
        """
        run_id = uuid4()
        thread_id = thread_id or str(uuid4())

        configurable = {"thread_id": thread_id}
        if agent_config:
            if overlap := configurable.keys() & agent_config.keys():
                raise AgentClientError(f"agent_config contains reserved keys: {overlap}")
            configurable.update(agent_config)

        kwargs = {
            "input": {"messages": [HumanMessage(content=message)]},
            "config": RunnableConfig(
                configurable=configurable,
                run_id=run_id,
            ),
        }

        try:
            for event in self.agent.stream_events(**kwargs, version="v2"):
                if not event:
                    continue

                new_messages = []
                # Yield messages written to the graph state after node execution finishes.
                if (
                    event["event"] == "on_chain_end"
                    # on_chain_end gets called a bunch of times in a graph execution
                    # This filters out everything except for "graph node finished"
                    and any(t.startswith("graph:step:") for t in event.get("tags", []))
                ):
                    if isinstance(event["data"]["output"], Command):
                        new_messages = event["data"]["output"].update.get("messages", [])
                    elif "messages" in event["data"]["output"]:
                        new_messages = event["data"]["output"]["messages"]

                # Also yield intermediate messages from agents.utils.CustomData.adispatch().
                if event["event"] == "on_custom_event" and "custom_data_dispatch" in event.get("tags", []):
                    new_messages = [event["data"]]

                for message in new_messages:
                    try:
                        chat_message = langchain_to_chat_message(message)
                        chat_message.run_id = str(run_id)
                    except Exception:
                        yield f"data: {json.dumps({'type': 'error', 'content': 'Unexpected error'})}\n\n"
                        continue
                    # LangGraph re-sends the input message, which feels weird, so drop it
                    if chat_message.type == "human" and chat_message.content == message:
                        continue
                    yield chat_message

                # Yield tokens streamed from LLMs.
                if (
                    event["event"] == "on_chat_model_stream"
                    and stream_tokens
                    and "llama_guard" not in event.get("tags", [])
                ):
                    content = remove_tool_calls(event["data"]["chunk"].content)
                    if content:
                        # Empty content in the context of OpenAI usually means
                        # that the model is asking for a tool to be invoked.
                        # So we only print non-empty content.
                        yield convert_message_content_to_string(content)
        except Exception as e:
            raise AgentClientError(f"Error streaming from agent: {e}") from e

    async def astream(
        self,
        message: str,
        thread_id: str | None = None,
        agent_config: dict[str, Any] | None = None,
        stream_tokens: bool = True,
    ) -> AsyncGenerator[ChatMessage | str, None]:
        """
        Stream the agent's response asynchronously.

        Each intermediate message of the agent process is yielded as a ChatMessage.
        If stream_tokens is True (the default value), the response will also yield
        content tokens from streaming models as they are generated.

        Args:
            message (str): The message to send to the agent
            thread_id (str, optional): Thread ID for continuing a conversation
            agent_config (dict[str, Any], optional): Additional configuration to pass through to the agent
            stream_tokens (bool, optional): Stream tokens as they are generated
                Default: True

        Returns:
            AsyncGenerator[ChatMessage | str, None]: The response from the agent
        """
        run_id = uuid4()
        thread_id = thread_id or str(uuid4())

        configurable = {"thread_id": thread_id}
        if agent_config:
            if overlap := configurable.keys() & agent_config.keys():
                raise AgentClientError(f"agent_config contains reserved keys: {overlap}")
            configurable.update(agent_config)

        kwargs = {
            "input": {"messages": [HumanMessage(content=message)]},
            "config": RunnableConfig(
                configurable=configurable,
                run_id=run_id,
            ),
        }

        try:
            async for event in self.agent.astream_events(**kwargs, version="v2"):
                if not event:
                    continue

                new_messages = []
                # Yield messages written to the graph state after node execution finishes.
                if (
                    event["event"] == "on_chain_end"
                    # on_chain_end gets called a bunch of times in a graph execution
                    # This filters out everything except for "graph node finished"
                    and any(t.startswith("graph:step:") for t in event.get("tags", []))
                ):
                    if isinstance(event["data"]["output"], Command):
                        new_messages = event["data"]["output"].update.get("messages", [])
                    elif "messages" in event["data"]["output"]:
                        new_messages = event["data"]["output"]["messages"]

                # Also yield intermediate messages from agents.utils.CustomData.adispatch().
                if event["event"] == "on_custom_event" and "custom_data_dispatch" in event.get("tags", []):
                    new_messages = [event["data"]]

                for message in new_messages:
                    try:
                        chat_message = langchain_to_chat_message(message)
                        chat_message.run_id = str(run_id)
                    except Exception:
                        yield f"data: {json.dumps({'type': 'error', 'content': 'Unexpected error'})}\n\n"
                        continue
                    # LangGraph re-sends the input message, which feels weird, so drop it
                    if chat_message.type == "human" and chat_message.content == message:
                        continue
                    yield chat_message

                # Yield tokens streamed from LLMs.
                if (
                    event["event"] == "on_chat_model_stream"
                    and stream_tokens
                    and "llama_guard" not in event.get("tags", [])
                ):
                    content = remove_tool_calls(event["data"]["chunk"].content)
                    if content:
                        # Empty content in the context of OpenAI usually means
                        # that the model is asking for a tool to be invoked.
                        # So we only print non-empty content.
                        yield convert_message_content_to_string(content)
        except Exception as e:
            raise AgentClientError(f"Error streaming from agent: {e}") from e

    def get_history(
        self,
        thread_id: str,
    ) -> ChatHistory:
        """
        Get chat history.

        Args:
            thread_id (str): Thread ID for identifying a conversation
        """
        try:
            state_snapshot = self.agent.get_state(
                config=RunnableConfig(
                    configurable={
                        "thread_id": thread_id,
                    }
                )
            )
            messages = state_snapshot.values["messages"]
            chat_messages = [langchain_to_chat_message(m) for m in messages]
            return ChatHistory(messages=chat_messages)
        except Exception as e:
            raise AgentClientError(f"Error getting history: {e}") from e


class AutoAgentClient:
    """Client for interacting with the AutoAgent directly."""

    def __init__(self, auto_agent) -> None:
        """
        Initialize the client.

        Args:
            auto_agent (AutoAgent): The auto agent to use.
        """
        self.auto_agent = auto_agent

    def retrieve_info(self) -> None:
        """Get information about the agent."""
        # This is a placeholder method that doesn't need to do anything
        # since we're directly using the agent
        pass

    async def ainvoke(
        self,
        message: str,
        thread_id: str | None = None,
        agent_config: dict[str, Any] | None = None,
    ) -> ChatMessage:
        """
        Invoke the auto agent asynchronously. Only the final message is returned.

        Args:
            message (str): The message to send to the agent
            thread_id (str, optional): Thread ID for continuing a conversation
            agent_config (dict[str, Any], optional): Additional configuration to pass through to the agent

        Returns:
            ChatMessage: The response from the agent
        """
        run_id = uuid4()
        thread_id = thread_id or str(uuid4())

        # Extract configuration for AutoAgent
        app_limit = agent_config.get("app_limit", 5) if agent_config else 5
        action_limit = agent_config.get("action_limit", 10) if agent_config else 10
        interactive = agent_config.get("interactive", False) if agent_config else False

        try:
            # Run the AutoAgent with the given task
            result = await self.auto_agent.run(
                task=message,
                app_limit=app_limit,
                action_limit=action_limit,
                interactive=interactive
            )
            
            # Create a ChatMessage from the result
            output = ChatMessage(
                type="ai",
                content=result,
                run_id=str(run_id)
            )
            return output
        except Exception as e:
            raise AgentClientError(f"Error invoking auto agent: {e}") from e

    def invoke(
        self,
        message: str,
        thread_id: str | None = None,
        agent_config: dict[str, Any] | None = None,
    ) -> ChatMessage:
        """
        Invoke the auto agent synchronously. Only the final message is returned.

        Args:
            message (str): The message to send to the agent
            thread_id (str, optional): Thread ID for continuing a conversation
            agent_config (dict[str, Any], optional): Additional configuration to pass through to the agent

        Returns:
            ChatMessage: The response from the agent
        """
        # For AutoAgent, we'll use the async version since it's designed for async operations
        return asyncio.run(self.ainvoke(message, thread_id, agent_config))

    def stream(
        self,
        message: str,
        thread_id: str | None = None,
        agent_config: dict[str, Any] | None = None,
        stream_tokens: bool = True,
    ) -> Generator[ChatMessage | str, None, None]:
        """
        Stream the auto agent's response synchronously.

        Note: AutoAgent doesn't support streaming in the same way as the react agent.
        This method yields the final result as a single message.

        Args:
            message (str): The message to send to the agent
            thread_id (str, optional): Thread ID for continuing a conversation
            agent_config (dict[str, Any], optional): Additional configuration to pass through to the agent
            stream_tokens (bool, optional): Not used for AutoAgent

        Returns:
            Generator[ChatMessage | str, None, None]: The response from the agent
        """
        run_id = uuid4()
        thread_id = thread_id or str(uuid4())

        # Extract configuration for AutoAgent
        app_limit = agent_config.get("app_limit", 5) if agent_config else 5
        action_limit = agent_config.get("action_limit", 10) if agent_config else 10
        interactive = agent_config.get("interactive", False) if agent_config else False

        try:
            # For AutoAgent, we'll run it synchronously and yield the result
            result = asyncio.run(self.auto_agent.run(
                task=message,
                app_limit=app_limit,
                action_limit=action_limit,
                interactive=interactive
            ))
            
            # Create a ChatMessage from the result
            output = ChatMessage(
                type="ai",
                content=result,
                run_id=str(run_id)
            )
            yield output
        except Exception as e:
            raise AgentClientError(f"Error streaming from auto agent: {e}") from e

    async def astream(
        self,
        message: str,
        thread_id: str | None = None,
        agent_config: dict[str, Any] | None = None,
        stream_tokens: bool = True,
    ) -> AsyncGenerator[ChatMessage | str, None]:
        """
        Stream the auto agent's response asynchronously.

        Note: AutoAgent doesn't support streaming in the same way as the react agent.
        This method yields the final result as a single message.

        Args:
            message (str): The message to send to the agent
            thread_id (str, optional): Thread ID for continuing a conversation
            agent_config (dict[str, Any], optional): Additional configuration to pass through to the agent
            stream_tokens (bool, optional): Not used for AutoAgent

        Returns:
            AsyncGenerator[ChatMessage | str, None]: The response from the agent
        """
        run_id = uuid4()
        thread_id = thread_id or str(uuid4())

        # Extract configuration for AutoAgent
        app_limit = agent_config.get("app_limit", 5) if agent_config else 5
        action_limit = agent_config.get("action_limit", 10) if agent_config else 10
        interactive = agent_config.get("interactive", False) if agent_config else False

        try:
            # Run the AutoAgent with the given task
            result = await self.auto_agent.run(
                task=message,
                app_limit=app_limit,
                action_limit=action_limit,
                interactive=interactive
            )
            
            # Create a ChatMessage from the result
            output = ChatMessage(
                type="ai",
                content=result,
                run_id=str(run_id)
            )
            yield output
        except Exception as e:
            raise AgentClientError(f"Error streaming from auto agent: {e}") from e

    def get_history(
        self,
        thread_id: str,
    ) -> ChatHistory:
        """
        Get chat history.

        Note: AutoAgent doesn't maintain conversation history in the same way.
        This method returns an empty history.

        Args:
            thread_id (str): Thread ID for identifying a conversation
        """
        # AutoAgent doesn't maintain conversation history
        return ChatHistory(messages=[])
