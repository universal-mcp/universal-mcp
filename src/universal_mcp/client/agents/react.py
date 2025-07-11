import json
from typing import Any

from loguru import logger

from universal_mcp.tools.adapters import ToolFormat
from universal_mcp.tools.manager import ToolManager

from .base import BaseAgent
from .llm import LLMClient


class ReActAgent(BaseAgent):
    def __init__(
        self, name: str, instructions: str, model: str, max_iterations: int = 10, tool_manager: ToolManager = None
    ):
        super().__init__(name, instructions, model)
        self.llm_client = LLMClient(model)
        self.max_iterations = max_iterations
        self.tool_manager = tool_manager
        logger.debug(f"Initialized ReActAgent: name={name}, model={model}")

    def _build_system_message(self) -> str:
        system_message = f"""You are {self.name}. {self.instructions}

You have access to various tools that can help you answer questions and complete tasks. When you need to use a tool:

1. Think about what information you need
2. Call the appropriate tool with the right parameters
3. Use the tool results to provide a comprehensive answer

Always explain your reasoning and be thorough in your responses. If you need to use multiple tools to answer a question completely, do so."""
        logger.debug(f"System message built: {system_message}")
        return system_message

    async def execute(self, user_input: str) -> str:
        """Process user input using native tool calling with ReAct logic"""

        logger.info(f"Processing user input: {user_input}")

        # Build messages for current request only
        messages = [
            {"role": "system", "content": self._build_system_message()},
            {"role": "user", "content": user_input},
        ]

        # Handle complete tool calling conversation loop
        tools = self.tool_manager.list_tools(format=ToolFormat.OPENAI) if self.tool_manager else None

        for iteration in range(self.max_iterations):
            logger.debug(f"Tool calling iteration {iteration + 1}/{self.max_iterations}")

            # Generate response with tools
            response = await self.llm_client.generate_response(messages, tools)

            # Return if no tool calls needed
            if not response.tool_calls:
                logger.info(f"LLM response received: {response.content}")
                return response.content

            # Add assistant message with tool calls
            messages.append(
                {
                    "role": "assistant",
                    "content": response.content,
                    "tool_calls": response.tool_calls,
                }
            )

            # Execute tool calls and add results
            for tool_call in response.tool_calls:
                self.cli.display_tool_call(tool_call.function.model_dump())
                tool_result = await self._execute_tool_call(tool_call)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result),
                    }
                )
                self.cli.display_tool_result(tool_result)

        # Generate final response after max iterations
        logger.warning(f"Max iterations ({self.max_iterations}) reached, generating final response")
        final_response = await self.llm_client.generate_response(messages)
        logger.info(f"Final LLM response received: {final_response.content}")
        return final_response.content

    async def _execute_tool_call(self, tool_call) -> Any:
        """Execute a single tool call with error handling."""
        function = tool_call.function
        tool_name = function.name

        try:
            # Parse arguments
            try:
                tool_args = json.loads(function.arguments)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON arguments for {tool_name}, using as query")
                tool_args = {"query": function.arguments}

            # Execute tool
            return await self.tool_manager.call_tool(tool_name, tool_args)

        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {e}"
            logger.error(error_msg)
            return error_msg
