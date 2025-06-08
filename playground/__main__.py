import os
import subprocess
import sys
import time

from loguru import logger
from opentelemetry import trace

from universal_mcp.config import ServerConfig
from universal_mcp.logger import setup_logger

tracer = trace.get_tracer(__name__)


def main():
    # --- OpenTelemetry Setup ---
    app_name = "universal-mcp-playground"
    otel_endpoint = None
    try:
        # Try to load config to get OTel endpoint
        # Assuming local_config.json is the source for server config in playground
        if os.path.exists("local_config.json"):
            server_config = ServerConfig.load_json_config("local_config.json")
            otel_endpoint = server_config.otel_exporter_otlp_endpoint
            app_name = server_config.name or app_name # Use server name if available
        else:
            logger.info("local_config.json not found, OpenTelemetry will not be initialized from server config.")
    except Exception as e:
        logger.warning(f"Failed to load ServerConfig for OpenTelemetry: {e}")

    # Setup logger (which also sets up OTel if endpoint is available)
    setup_logger(otel_exporter_otlp_endpoint=otel_endpoint, app_name=app_name)
    # --- End OpenTelemetry Setup ---

    with tracer.start_as_current_span("app.startup"):
        processes = []

    # Start MCP server first
    # Ask the user if they want to run the MCP server
    run_mcp_server = input("Do you want to run the MCP server? (y/n): ")
    if run_mcp_server == "y":
        mcp_process = subprocess.Popen(["universal_mcp", "run", "-c", "local_config.json"])
        processes.append(mcp_process)
        time.sleep(6)  # Give MCP server time to start
        logger.info("MCP server started")

        streamlit_cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            os.path.join("playground", "streamlit.py"),
        ]
        processes.append(subprocess.Popen(streamlit_cmd, env=os.environ))
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
