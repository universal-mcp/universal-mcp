import subprocess
import time

from loguru import logger


def main():
    processes = []

    # Start MCP server first
    mcp_process = subprocess.Popen(["universal_mcp", "run", "-c", "local_config.json"])
    processes.append(mcp_process)
    time.sleep(3)  # Give MCP server time to start
    logger.info("MCP server started")

    # Start FastAPI app second
    fastapi_process = subprocess.Popen(["fastapi", "run", "src/playground"])
    processes.append(fastapi_process)
    time.sleep(3)  # Give FastAPI time to start
    logger.info("FastAPI app started")
    # Start Streamlit app last
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
