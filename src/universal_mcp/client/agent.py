import json

from loguru import logger
from mcp.server import Server as MCPServer
from openai import AsyncOpenAI

from universal_mcp.config import LLMConfig


class ChatSession:
    """Orchestrates the interaction between user, LLM, and tools."""

    def __init__(self, mcp_server: MCPServer, llm: LLMConfig | None) -> None:
        self.mcp_server: MCPServer = mcp_server
        self.llm: AsyncOpenAI | None = AsyncOpenAI(api_key=llm.api_key, base_url=llm.base_url) if llm else None
        self.model = llm.model if llm else None

    async def run(self, messages, tools) -> None:
        """Run the chat session."""
        llm_response = await self.llm.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        tool_calls = llm_response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                result = await self.mcp_server.call_tool(
                    tool_name=tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments) if tool_call.function.arguments else {},
                )
                result_content = [rc.text for rc in result.content] if result.content else "No result"
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": result_content,
                    }
                )
        else:
            messages.append(llm_response.choices[0].message)
        return messages

    async def interactive_loop(self) -> None:
        """Main chat session handler."""
        all_openai_tools = await self.mcp_server.list_tools(format="openai")
        system_message = "You are a helpful assistant"
        messages = [{"role": "system", "content": system_message}]

        print("\n🎯 Interactive MCP Client")
        print("Commands:")
        print("  list - List available tools")
        print("  call <tool_name> [args] - Call a tool")
        print("  quit - Exit the client")
        print()
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in {"quit", "exit"}:
                    logger.info("\nExiting...")
                    break
                elif user_input.lower() == "list":
                    tools = await self.mcp_server.list_tools()
                    print("\nAvailable tools:")
                    for tool in tools:
                        print(f"  {tool.name}")
                    continue
                elif user_input.startswith("call "):
                    parts = user_input.split(maxsplit=2)
                    tool_name = parts[1] if len(parts) > 1 else ""

                    if not tool_name:
                        print("❌ Please specify a tool name")
                        continue

                    # Parse arguments (simple JSON-like format)
                    arguments = {}
                    if len(parts) > 2:
                        try:
                            arguments = json.loads(parts[2])
                        except json.JSONDecodeError:
                            print("❌ Invalid arguments format (expected JSON)")
                            continue
                    await self.mcp_server.call_tool(tool_name, arguments)

                messages.append({"role": "user", "content": user_input})

                messages = await self.run(messages, all_openai_tools)
                print("\nAssistant: ", messages[-1]["content"])

            except KeyboardInterrupt:
                print("\nExiting...")
                break
