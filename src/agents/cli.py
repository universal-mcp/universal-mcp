from typer import Typer

from agents import ReactAgent
from universal_mcp.logger import setup_logger

app = Typer()


@app.command(
    help="Run the agent CLI",
    epilog="""
    Example:
    mcp client run --config client_config.json
    """,
)
def run():
    """Run the agent CLI"""
    import asyncio

    setup_logger(log_file=None, level="WARNING")

    agent = ReactAgent("React Agent", "You are a helpful assistant", "openrouter/auto")
    asyncio.run(agent.run_interactive())


if __name__ == "__main__":
    app()
