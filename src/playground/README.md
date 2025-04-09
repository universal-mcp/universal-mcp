## Running the Playground

### Automated Startup (Recommended)

To easily start all necessary services (MCP Server, FastAPI Backend, Streamlit Frontend), you can use the provided Python startup script. This script will attempt to open each service in sequence and ensures they are terminated gracefully upon interruption.

**Prerequisites:**

*   Python 3 installed and available in your PATH.
*   All project dependencies installed (ensure you've run `pip install ...` for all requirements).
*   **`local_config.json` file:** This configuration file for the MCP server must exist in the **project root directory**. It should contain a JSON array defining the MCP tools to load. For example:
    ```json
    {
        "name": "Local Server",
        "description": "Local server for testing",
        "type": "local",
        "transport": "sse",
        "apps": [
            {
                "name": "zenquotes"
            }
        ]
    }
    ```
    *(Adapt the content based on the actual MCP tools you intend to use.)*
*   A compatible terminal environment for the script:
    *   On **macOS**, requires the standard `Terminal.app`.
    *   On **Linux**, assumes `gnome-terminal` is available (common on Ubuntu/Fedora). You may need to modify `src/playground/__main__.py` if you use a different terminal like `konsole` or `xfce4-terminal`.
    *   On **Windows**, requires the standard `cmd.exe`.

**Instructions:**

1.  Open your terminal application.
2.  Navigate (`cd`) to the **root directory** of this project (the directory containing the `src/` folder and `local_config.json`).
3.  Execute the startup script using Python:

    ```bash
    python src/playground
    ```

    *(Note: If your system uses `python3` to invoke Python 3, use that command instead: `python3 src/playground`)*

After running the command, you should see messages indicating that the components are being launched.

### Manual Startup (Alternative)

If you prefer, or if the automated script does not work on your specific system configuration, you can still start each component manually. Make sure you run each command from the **project root directory** in a separate terminal window:

1.  **Terminal 1 (MCP Server):**
    *(Ensure `local_config.json` exists in the project root as described above)*
    ```bash
    universal_mcp run -c local_config.json
    ```
2.  **Terminal 2 (FastAPI App):**
    ```bash
    fastapi run src/playground
    ```
3.  **Terminal 3 (Streamlit App):**
    ```bash
    streamlit run src/playground/streamlit.py
    ```

### Stopping the Services

To stop the running services, go to each of the terminal windows that were opened (either by the script or manually) and press `Ctrl + C`.