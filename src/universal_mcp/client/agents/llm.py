import json
from typing import Any

from loguru import logger
from openai import OpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionToolParam,
)

from universal_mcp.tools.adapters import ToolFormat
from universal_mcp.tools.manager import ToolManager


class LLMClient:
    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI()
        logger.info(f"LLMClient initialized with model: {self.model}")

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        tools: list[ChatCompletionToolParam] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> ChatCompletionMessage:
        """Generate response using OpenAI with native tool calling"""
        try:
            logger.debug(f"Generating response with messages: {messages}")
            kwargs = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
                logger.debug(f"Using tools: {tools}")
            response: ChatCompletion = self.client.chat.completions.create(**kwargs)
            logger.debug(f"OpenAI response: {response}")
            choice = response.choices[0]
            message: ChatCompletionMessage = choice.message
            logger.info(f"Generated message: {message}")
            return message
        except Exception as e:
            logger.error(f"Error in generate_response: {e}")
            raise e

    async def handle_tool_calls(
        self, tool_calls: list[ChatCompletionToolParam], tool_manager: ToolManager
    ) -> list[dict[str, Any]]:
        """Handle tool calls"""
        messages: list[dict[str, Any]] = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments
            logger.info(f"Handling tool call: {tool_name} with args: {tool_args}")
            tool_result = await tool_manager.call_tool(tool_name, tool_args)
            logger.debug(f"Tool result for {tool_name}: {tool_result}")
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(tool_result)})
        return messages

    async def generate_response_with_tool_results(
        self, messages: list[dict[str, str]], tool_manager: ToolManager, max_iterations: int = 5
    ) -> ChatCompletionMessage:
        """Handle complete tool calling conversation loop using OpenAI"""
        conversation = messages.copy()
        iteration = 0
        tools = tool_manager.list_tools(format=ToolFormat.OPENAI)
        logger.info(f"Starting tool calling loop with max_iterations={max_iterations}")

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Iteration {iteration}: Generating response with conversation: {conversation}")

            # Generate response with tools
            response = await self.generate_response(conversation, tools)

            # If no tool calls, return the response
            tool_calls = response.tool_calls
            if not tool_calls:
                logger.info("No tool calls detected, returning response.")
                return response

            logger.info(f"Tool calls detected: {tool_calls}")

            # Add assistant message with tool calls
            assistant_msg = {"role": "assistant", "content": response.content}
            if tool_calls:
                assistant_msg["tool_calls"] = tool_calls
            conversation.append(assistant_msg)

            # Execute tool calls and add results
            for tool_call in tool_calls:
                function = tool_call.function
                tool_name = function.name
                arguments = function.arguments
                logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")
                try:
                    tool_args = json.loads(arguments)
                except Exception as e:
                    logger.warning(f"Failed to parse tool arguments as JSON: {arguments}. Error: {e}")
                    tool_args = {"query": arguments}
                # Execute the tool
                try:
                    tool_result = await tool_manager.call_tool(tool_name, tool_args)
                    logger.debug(f"Tool result for {tool_name}: {tool_result}")
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}")
                    tool_result = f"Error executing tool {tool_name}: {e}"
                # Add tool result to conversation
                conversation.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(tool_result)})
            # Continue the conversation loop

        logger.info("Max iterations reached or tool loop complete. Generating final response.")
        # Final response after tool execution
        return await self.generate_response(conversation)
