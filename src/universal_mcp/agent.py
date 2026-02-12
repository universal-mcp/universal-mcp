"""Claude Code agent with Universal MCP CLI access using the Claude Agent SDK."""

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)
from loguru import logger


async def run_agent_query(prompt: str, model: str | None = None) -> None:
    """Run a single agent query with the Claude Agent SDK.

    Args:
        prompt: The prompt to send to the agent.
        model: Optional model to use (e.g., 'sonnet', 'opus').
    """
    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "Read", "Write", "Glob", "Grep"],
        permission_mode="acceptEdits",
        max_turns=25,
    )
    if model:
        options.model = model

    client = ClaudeSDKClient(options=options)
    await client.connect()

    try:
        await client.query(prompt=prompt)

        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
                    elif isinstance(block, ToolUseBlock) and block.name == "Bash":
                        cmd = block.input.get("command", "")
                        logger.info(f"Running: {cmd}")
            elif isinstance(message, ResultMessage):
                # End of turn
                break
    finally:
        await client.disconnect()


async def run_interactive_agent(model: str | None = None) -> None:
    """Run an interactive turn-by-turn conversation with the agent.

    Args:
        model: Optional model to use (e.g., 'sonnet', 'opus').
    """
    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "Read", "Write", "Glob", "Grep"],
        permission_mode="acceptEdits",
        max_turns=25,
    )
    if model:
        options.model = model

    client = ClaudeSDKClient(options=options)
    await client.connect()

    print("\n💬 Interactive Universal MCP Agent")
    print("Type your message and press Enter. Type 'exit' or 'quit' to end the session.\n")

    try:
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ("exit", "quit", "bye"):
                    print("\nGoodbye! 👋")
                    break

                # Send prompt and receive responses
                await client.query(prompt=user_input)

                async for message in client.receive_messages():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                print(f"\nAgent: {block.text}\n")
                            elif isinstance(block, ToolUseBlock) and block.name == "Bash":
                                cmd = block.input.get("command", "")
                                logger.info(f"Running: {cmd}")
                    elif isinstance(message, ResultMessage):
                        # End of turn - go back to waiting for user input
                        break

            except EOFError:
                print("\nGoodbye! 👋")
                break
    finally:
        await client.disconnect()


def start_agent(prompt: str | None = None, model: str | None = None) -> int:
    """Start a Claude Code agent with Universal MCP CLI access.

    Args:
        prompt: Optional prompt for single-turn mode. If None, starts interactive mode.
        model: Optional model to use (e.g., 'sonnet', 'opus').

    Returns:
        Process return code.
    """
    try:
        if prompt:
            # Single-turn mode: run one query and exit
            anyio.run(run_agent_query, prompt, model)
        else:
            # Interactive mode: turn-by-turn conversation
            anyio.run(run_interactive_agent, model)
        return 0
    except KeyboardInterrupt:
        logger.info("Agent session ended by user")
        return 0
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return 1
