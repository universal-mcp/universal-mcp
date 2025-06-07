import asyncio
import os
import sys

from loguru import logger
from pydantic import ValidationError

from universal_mcp.client.agent import ChatSession
from universal_mcp.client.client import MultiClientServer
from universal_mcp.config import ClientConfig


async def main() -> None:
    """Initialize and run the chat session."""
    # Load settings and config using Pydantic BaseSettings

    config_path = os.getenv("MCP_CONFIG_PATH", "servers.json")
    try:
        app_config = ClientConfig.load_json_config(config_path)
    except (FileNotFoundError, ValidationError) as e:
        logger.error(f"Error loading config: {e}")
        sys.exit(1)

    async with MultiClientServer(app_config.mcpServers) as mcp_server:
        chat_session = ChatSession(mcp_server, app_config.llm)
        await chat_session.interactive_loop()


if __name__ == "__main__":
    asyncio.run(main())
