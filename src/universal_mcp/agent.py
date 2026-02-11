"""Claude Code agent with Universal MCP CLI access using the Claude Agent SDK."""

import anyio
from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, ToolUseBlock, query
from loguru import logger

AGENT_SYSTEM_PROMPT = """You are a helpful assistant with access to the Universal MCP CLI tool called `unsw`.

## Available Commands

### App Management
- `unsw app install <name>` - Install an MCP application (e.g., `unsw app install github`)
- `unsw app install <url> --transport http` - Install from a remote MCP server URL
- `unsw app remove <slug>` - Remove an application
- `unsw app authorize <slug>` - Authorize an app with credentials
- `unsw app list` - List installed applications
- `unsw app list-tools` - List available tools (use `--app <slug>` to filter)
- `unsw app search-tools <query>` - Search for tools

### Server Management
- `unsw server start` - Start the MCP server

### Cron Management
- `unsw cron list` - List scheduled tasks
- `unsw cron add` - Add a scheduled task
- `unsw cron remove <name>` - Remove a scheduled task

### Status
- `unsw status` - Show current SDK status

### Skills Management
- `unsw skills list` - List installed Claude Code skills
- `unsw skills search <query>` - Search installed skills
- `unsw skills install <source>` - Install a skill from local path or GitHub URL
- `unsw skills remove <name>` - Remove an installed skill
- `unsw skills scan` - Scan and update skill registry
- `unsw skills info <name>` - Show skill details

## How to Use

1. You can run any of these commands using your Bash tool
2. To help users set up MCP apps: add the app, authorize it, then list its tools
3. To help users manage skills: search, install from GitHub URLs or local paths, list installed skills
4. Always use the `unsw` command - it's the CLI for Universal MCP

## Guidelines
- Be helpful and proactive in suggesting MCP apps and skills
- When a user wants to use an API, suggest adding the relevant MCP app
- When installing skills, prefer global scope unless the user specifies project scope
- Show users what tools are available after adding an app
"""


async def run_agent_query(prompt: str, model: str | None = None) -> None:
    """Run a single agent query with the Claude Agent SDK.

    Args:
        prompt: The prompt to send to the agent.
        model: Optional model to use (e.g., 'sonnet', 'opus').
    """
    options = ClaudeAgentOptions(
        system_prompt=AGENT_SYSTEM_PROMPT,
        allowed_tools=["Bash", "Read", "Write", "Glob", "Grep"],
        permission_mode="acceptEdits",
        max_turns=25,
    )
    if model:
        options.model = model

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock) and block.name == "Bash":
                    cmd = block.input.get("command", "")
                    logger.info(f"Running: {cmd}")


def start_agent(prompt: str | None = None, model: str | None = None) -> int:
    """Start a Claude Code agent with Universal MCP CLI access.

    Args:
        prompt: Optional initial prompt to send to the agent.
        model: Optional model to use (e.g., 'sonnet', 'opus').

    Returns:
        Process return code.
    """
    if not prompt:
        prompt = "Help me manage my Universal MCP applications and skills. What would you like to do?"

    try:
        anyio.run(run_agent_query, prompt, model)
        return 0
    except KeyboardInterrupt:
        logger.info("Agent session ended by user")
        return 0
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return 1
