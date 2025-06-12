import json

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

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        tools: list[ChatCompletionToolParam] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> ChatCompletionMessage:
        """Generate response using OpenAI with native tool calling"""
        try:
            kwargs = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            response: ChatCompletion = self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            message: ChatCompletionMessage = choice.message
            return message
        except Exception as e:
            raise e

    async def generate_response_with_tool_results(
        self, messages: list[dict[str, str]], tool_manager: ToolManager, max_iterations: int = 5
    ) -> ChatCompletionMessage:
        """Handle complete tool calling conversation loop using OpenAI"""
        conversation = messages.copy()
        iteration = 0
        tools = tool_manager.list_tools(format=ToolFormat.OPENAI)

        while iteration < max_iterations:
            iteration += 1

            # Generate response with tools
            response = await self.generate_response(conversation, tools)

            # If no tool calls, return the response
            tool_calls = response.tool_calls
            if not tool_calls:
                return response

            # Add assistant message with tool calls
            assistant_msg = {"role": "assistant", "content": response.content}
            if tool_calls:
                assistant_msg["tool_calls"] = tool_calls
            conversation.append(assistant_msg)

            # Execute tool calls and add results
            for tool_call in tool_calls:
                # OpenAI tool_call is a dict with keys: id, type, function
                # function: {name, arguments}
                function = tool_call.function
                tool_name = function.name
                arguments = function.arguments
                try:
                    tool_args = json.loads(arguments)
                except Exception:
                    tool_args = {"query": arguments}
                # Execute the tool
                tool_result = await tool_manager.call_tool(tool_name, tool_args)
                # Add tool result to conversation
                conversation.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(tool_result)})
            # Continue the conversation loop

        # Final response after tool execution
        return await self.generate_response(conversation)
