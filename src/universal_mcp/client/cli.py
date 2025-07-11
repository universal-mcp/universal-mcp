from typer import Typer

from universal_mcp.client.agents import ReActAgent
from universal_mcp.config import ClientConfig
from universal_mcp.logger import setup_logger
from universal_mcp.servers.server import load_from_local_config
from universal_mcp.tools.manager import ToolManager

app = Typer()


@app.command()
def run(config: str = "client_config.json"):
    """Run the agent CLI"""
    import asyncio

    setup_logger(log_file=None, level="WARNING")
    config = ClientConfig.load_json_config(config)
    tool_manager = ToolManager()
    load_from_local_config(config, tool_manager)

    agent = ReActAgent("ReAct Agent", "You are a helpful assistant", config.model, tool_manager=tool_manager)
    asyncio.run(agent.run_interactive())


if __name__ == "__main__":
    app()
