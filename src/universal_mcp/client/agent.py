import json

from loguru import logger
from mcp.server import Server as MCPServer
from openai import AsyncOpenAI

from universal_mcp.config import LLMConfig


class ChatSession:
    """Manages an interactive chat session with LLM and tool integration.

    This class orchestrates the conversation flow between a user and a
    Large Language Model (LLM). It is responsible for:
    - Initializing and holding the MCP server instance for tool access.
    - Configuring and interacting with the specified LLM (e.g., OpenAI).
    - Processing messages from the LLM, identifying tool call requests.
    - Executing requested tools via the MCP server.
    - Formatting tool results and sending them back to the LLM.
    - Running an interactive command-line loop for user interaction.

    Attributes:
        mcp_server (MCPServer): An instance of `mcp.server.Server` used to
            list and call available tools.
        llm (AsyncOpenAI | None): An instance of `openai.AsyncOpenAI` configured
            for communicating with the LLM. This is None if no LLM
            configuration is provided.
        model (str | None): The specific model name (e.g., "gpt-4-turbo")
            to be used for LLM completions. This is None if no LLM
            is configured.
    """

    def __init__(self, mcp_server: MCPServer, llm_config: LLMConfig | None) -> None:
        """Initializes the ChatSession.

        Args:
            mcp_server (MCPServer): The MCP server instance that provides
                access to tools.
            llm_config (LLMConfig | None): Configuration object for the LLM.
                If None, LLM-based interactions will be disabled.
        """
        self.mcp_server: MCPServer = mcp_server
        if llm_config:
            self.llm: AsyncOpenAI | None = AsyncOpenAI(
                api_key=llm_config.api_key, base_url=llm_config.base_url
            )
            self.model: str | None = llm_config.model
        else:
            self.llm = None
            self.model = None

    async def run(self, messages: list[dict], tools: list[dict]) -> list[dict]:
        """Processes a single turn in the chat conversation with the LLM.

        This method sends the current conversation history (`messages`) and
        available `tools` to the configured LLM. If the LLM's response
        includes tool call requests, this method executes those tools via
        the `mcp_server`, appends the tool results to the conversation history,
        and then returns the updated history. If no tool calls are made,
        the LLM's direct response is appended.

        Args:
            messages (list[dict]): A list of message objects representing the
                current conversation history, formatted for the LLM API.
            tools (list[dict]): A list of tool definitions, formatted for
                the LLM API, that the LLM can request to call.

        Returns:
            list[dict]: The updated list of messages, including the LLM's
                        response and any tool call results. Returns the original
                        messages if LLM is not configured.
        """
        if not self.llm or not self.model:
            logger.warning("LLM not configured. Skipping LLM interaction.")
            return messages
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
        """Runs an interactive command-line chat loop.

        This method provides a text-based interface for users to interact
        with the configured LLM and tools. Users can type messages,
        list available tools via the `list` command, directly call tools
        using `call <tool_name> [json_args]`, or exit with `quit`.

        The conversation history is maintained, and LLM responses (including
        those after tool calls) are printed to the console.
        Requires the LLM to be configured to function fully.
        """
        if not self.llm:
            logger.error(
                "LLM not configured. Please provide LLM configuration to use the interactive loop."
            )  # noqa: E501
            return

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
