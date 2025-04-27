import subprocess
import time

from loguru import logger


def main():
    processes = []

    # Start MCP server first
    # Ask the user if they want to run the MCP server
    run_mcp_server = input("Do you want to run the MCP server? (y/n): ")
    if run_mcp_server == "y":
        mcp_process = subprocess.Popen(["universal_mcp", "run", "-c", "local_config.json"])
        processes.append(mcp_process)
        time.sleep(6)  # Give MCP server time to start
        logger.info("MCP server started")

    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "src/playground/streamlit.py"]
    )
    processes.append(streamlit_process)
    logger.info("Streamlit app started")
    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()
            p.wait()


if __name__ == "__main__":
    main()
