import subprocess
import platform
import time
import os
import shlex

def launch_command_in_new_terminal(command, title="Command Output"):
    """
    Launches a command in a new terminal window.
    Handles macOS, Linux (gnome-terminal), and Windows.
    Keeps the terminal window open after the command finishes.
    Assumes this script is run from the project root directory.
    """
    system = platform.system()
    project_dir = os.getcwd()

    print(f"Attempting to launch '{title}' from CWD: {project_dir}...")

    try:
        if system == "Darwin":  # macOS
            applescript_command = f'''
            tell application "Terminal"
                activate
                do script "cd '{project_dir}' && echo '--- {title} ---' && {command} ; exec bash"
            end tell
            '''
            subprocess.Popen(['osascript', '-e', applescript_command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        elif system == "Linux":
            # Assumes gnome-terminal. Adapt if using konsole, xfce4-terminal, etc.
            full_cmd = f'cd "{project_dir}" && echo "--- {title} ---" && {command} ; exec bash'
            terminal_cmd = ["gnome-terminal", "--", "bash", "-c", full_cmd]
            subprocess.Popen(terminal_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        elif system == "Windows":
            full_cmd = f'cd /d "{project_dir}" && echo "--- {title} ---" && {command}'
            subprocess.Popen(f'start "{title}" cmd /k "{full_cmd}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        else:
            print(f"Warning: Unsupported operating system ({system}). Cannot launch in new terminal.")
            return False

        print(f"Launched '{title}' in a new terminal.")
        return True

    except FileNotFoundError:
        print("Error: Terminal emulator (e.g., gnome-terminal on Linux, Terminal.app on macOS) not found or osascript failed.")
        print(f"Attempted to run: {command}")
        return False
    except Exception as e:
        print(f"An error occurred while trying to launch '{title}': {e}")
        return False


if __name__ == "__main__":
    # Define the commands relative to the project root (which is the CWD)
    mcp_command = "universal_mcp run -s local -c local_config.json -t sse"
    # fastapi needs the path relative to the CWD (project root)
    fastapi_command = "fastapi run src/playground"
    # streamlit needs the path relative to the CWD (project root)
    streamlit_command = "streamlit run src/playground/streamlit.py"

    commands_to_launch = [
        {"command": mcp_command, "title": "MCP Server"},
        {"command": fastapi_command, "title": "FastAPI App"},
        {"command": streamlit_command, "title": "Streamlit App"},
    ]

    print("Starting Playground Components...")
    print(f"(Script executed from: {os.path.dirname(__file__)})") # Shows where the .py file is
    print(f"(Commands will run in CWD: {os.getcwd()})") # Shows the crucial CWD
    print("-" * 30)

    for item in commands_to_launch:
        success = launch_command_in_new_terminal(item["command"], item["title"])
        if success:
            time.sleep(2) # Stagger launches slightly
        else:
            print(f"Failed to launch {item['title']} in a new terminal.")
            # Optionally add 'break' here if one failure should stop the others

    print("-" * 30)
    print("All components have been launched (or attempted).")
    print("Check the new terminal windows for output.")