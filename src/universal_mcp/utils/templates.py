import ast


def extract_class_name(file_path):
    """Extract the first class name from a Python file."""
    with open(file_path) as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            return node.name
    raise ValueError("No class found in app.py")

def generate_app_py_template(app_class_name: str, app_name:str) -> str:
    return f"""from universal_mcp.applications.application import APIApplication
    
class {app_class_name}(APIApplication):
    def __init__(self, **kwargs) -> None:
        super().__init__(name="{app_name}", **kwargs)

    def run(self):
        print('Running {app_class_name}')
        
    def list_tools(self):
        return [self.run]
"""

def generate_test_template(app_name: str, app_class: str) -> str:
    return f"""import pytest

from {app_name}.app import {app_class}

@pytest.fixture
def app_instance():
    \"\"\"Provides a {app_class} instance for tests.\"\"\"
    return {app_class}()

def test_{app_name}_app_initialization(app_instance):
    \"\"\"
    Test that the {app_class} instance is initialized correctly with a name.
    \"\"\"
    assert hasattr(app_instance, 'name'), "Application instance should have a 'name' attribute."
    assert isinstance(app_instance.name, str), "Application name should be a string."
    assert app_instance.name.strip() != "", "Application name should not be empty."
    assert app_instance.name == "{app_name}", "{app_class} instance has unexpected name."

def test_{app_name}_tool_docstrings_format(app_instance):
    \"\"\"
    Test that each tool method in {app_class} has a well-formatted docstring,
    including summary, Args, Returns, and Tags sections.
    Checks for Raises section optionally.
    \"\"\"
    tools = app_instance.list_tools()
    assert isinstance(tools, list), "list_tools() should return a list."
    assert len(tools) > 0, "list_tools() should return at least one tool."

    for tool in tools:
        tool_name = getattr(tool, '__name__', 'Unknown Tool')
        docstring = tool.__doc__
        assert docstring is not None, f"Tool '{{tool_name}}' is missing a docstring."
        assert isinstance(docstring, str), f"Docstring for '{{tool_name}}' should be a string."

        lines = docstring.strip().split('\\n')
        assert len(lines) > 0, f"Docstring for '{{tool_name}}' is empty after stripping whitespace."

        summary_line = lines[0].strip()
        assert summary_line != "", f"Docstring for '{{tool_name}}' is missing a summary line."

        docstring_lower = docstring.lower()
        assert "args:" in docstring_lower, f"Docstring for '{{tool_name}}' is missing 'Args:' section."
        assert "returns:" in docstring_lower, f"Docstring for '{{tool_name}}' is missing 'Returns:' section."
        assert "raises:" in docstring_lower, f"Docstring for '{{tool_name}}' is missing 'Raises:' section."
        assert "tags:" in docstring_lower, f"Docstring for '{{tool_name}}' is missing 'Tags:' section."

def test_{app_name}_tools_are_callable(app_instance):
    \"\"\"
    Test that each tool method returned by list_tools in {app_class} is callable.
    \"\"\"
    tools = app_instance.list_tools()
    assert isinstance(tools, list), "list_tools() should return a list."

    for tool in tools:
        tool_name = getattr(tool, '__name__', 'Unknown Tool')
        assert callable(tool), f"Tool '{{tool_name}}' is not callable."
"""

def generate_pyproject_template(app_name: str) -> str:
    return f"""[project]
name = "{app_name}"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
authors = [
    {{ name = "Manoj Bajaj", email = "manojbajaj95@gmail.com" }}
]
requires-python = ">=3.13"
dependencies = [
    "universal-mcp",
    "pytest"
]

[project.scripts]
universal-mcp-{app_name} = "universal_mcp_{app_name}:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""

def generate_main_py_template(app_name: str, app_class: str, integration_type: str, integration_class: str | None) -> str:
    app_py_relative_import = f"{app_name}.app"

    if integration_type == "none":
        return f"""from universal_mcp.servers.server import SingleMCPServer

from {app_py_relative_import} import {app_class}

app_instance = {app_class}()

mcp = SingleMCPServer(
    app_instance=app_instance
)

if __name__ == "__main__":
    print(f"Starting {{mcp.name}}...")
    mcp.run()
"""

    elif integration_type == "api_key":
        return f"""from universal_mcp.servers.server import SingleMCPServer
from universal_mcp.integrations.integration import {integration_class}
from universal_mcp.stores.store import EnvironmentStore

from {app_py_relative_import} import {app_class}

env_store = EnvironmentStore()
integration_instance = {integration_class}(name="{app_name.upper()}_API_KEY", store=env_store)
app_instance = {app_class}(integration=integration_instance)

mcp = SingleMCPServer(
    app_instance=app_instance,
)

if __name__ == "__main__":
    mcp.run()
"""

    elif integration_type == "agentr":
        return f"""from universal_mcp.servers.server import SingleMCPServer
from universal_mcp.integrations.agentr import {integration_class}
from universal_mcp.stores.store import EnvironmentStore

from {app_py_relative_import} import {app_class}

env_store = EnvironmentStore()
integration_instance = {integration_class}(name="{app_name.lower()}", store=env_store)
app_instance = {app_class}(integration=integration_instance)

mcp = SingleMCPServer(
    app_instance=app_instance,
)

if __name__ == "__main__":
    mcp.run()
"""
    # elif integration_type == "oauth":
#             main_py_content = f"""from universal_mcp.servers.server import SingleMCPServer
# from universal_mcp.integrations.integration import {integration_class}
# from universal_mcp.stores.store import EnvironmentStore
# from {app_name}.app import {app_class}
# env_store = EnvironmentStore()
# integration_instance = {integration_class}(name=\"{app_name.upper()}_OAUTH\", store=env_store)
# app_instance = {app_class}(integration=integration_instance)
# mcp = SingleMCPServer(
#     app_instance=app_instance,
# )
# if __name__ == \"__main__\":
#     mcp.run()
# """

def generate_readme_template(app_name: str) -> str:
    return f"""# 🚀 {app_name.upper()} API Project

Welcome to the **{app_name.upper()}** API project!

This project provides a starting point for your API application, generated automatically by **MCP CLI** to help you kickstart your development quickly.

---

## 📋 Prerequisites

Before you begin, ensure you have met the following requirements:

*   **Python 3.11+** (Recommended)
*   **[uv](https://github.com/astral-sh/uv)** installed globally (`pip install uv`)

---

## 🛠️ Setup Instructions

Follow these steps to get the development environment up and running:

### 1. Sync Project Dependencies

Navigate to the project root directory (where `pyproject.toml` is located).

```bash
uv sync
```
This command uses `uv` to install all dependencies listed in `pyproject.toml` into a virtual environment (`.venv`) located in the project root.

### 2. Activate the Virtual Environment

Activating the virtual environment ensures that you are using the project's specific dependencies and Python interpreter.

- On **Linux/macOS**:

```bash
source .venv/bin/activate
```

- On **Windows**:

```bash
.venv\\Scripts\\activate
```

### 3. Start the MCP Inspector

Use the MCP CLI to start the application in development mode.

```bash
mcp dev src/{app_name}/__main__.py
```

The MCP inspector should now be running. Check the console output for the exact address and port.

---

## 🚀 Usage

Once the server is running, you can test the tools and interact with them.

---

## 📁 Project Structure

The generated project has a standard layout:

```
.
├── src/                  # Source code directory
│   └── {app_name}/
│       ├── __init__.py
│       └── __main__.py   # Server is launched here
│       └──   app.py      # Application tools are defined here
├── tests/                # Directory for project tests
├── .env                  # Environment variables (for local development)
├── pyproject.toml        # Project dependencies managed by uv
├── README.md             # This file
```

---

## ➡️ Next Steps

---

## 📄 License

---

_This project was generated using **MCP CLI** — Happy coding! 🚀_
"""

def generate_push_script_template(app_name: str) -> str:
    """Generate a shell script template to push the project to AgentrDev GitHub org."""
    repo_name = f"universal-mcp-{app_name}"
    org_name = "AgentrDev"

    return f"""#!/bin/bash

# Script to push the local project '{repo_name}' to the '{org_name}' GitHub organization.
# Requires GitHub CLI (gh) to be installed and authenticated with access to the organization.

# --- Configuration ---
ORG_NAME="{org_name}"
REPO_NAME="{repo_name}"
VISIBILITY="private" # Or 'public' or 'internal' as needed

# --- Script ---

echo "Navigating to project directory..."
# Assuming the script is run from the root of the project directory
PROJECT_ROOT="$(pwd)"
echo "Project root: $PROJECT_ROOT"

# Check if Git is initialized, if not, initialize it
if [ ! -d "$PROJECT_ROOT/.git" ]; then
  echo "Initializing Git repository..."
  git init
  if [ $? -ne 0 ]; then echo "Error: git init failed. Exiting."; exit 1; fi
else
  echo "Git repository already initialized."
fi

# Add all files and commit (initial commit message)
echo "Adding files and creating initial commit..."
git add .
git commit -m "Initial commit of {app_name} project"
# Check commit status - ignore if no changes were added
if [ $? -eq 0 ]; then
    echo "Commit successful."
elif [ $? -eq 1 ]; then
    echo "Warning: No changes to commit. Continuing..."
else
    echo "Error: git commit failed. Exiting."; exit 1;
fi


# Check if the remote 'origin' already exists
if git remote add origin https://github.com/$ORG_NAME/$REPO_NAME 2>/dev/null; then
  echo "Remote 'origin' added."
else
  echo "Remote 'origin' already exists or failed to add. Proceeding with push."
  # Check if the existing remote origin is the correct one (optional but good practice)
  CURRENT_REMOTE=$(git remote get-url origin)
  EXPECTED_REMOTE="https://github.com/$ORG_NAME/$REPO_NAME"
  if [ "$CURRENT_REMOTE" != "$EXPECTED_REMOTE" ] && [ "$CURRENT_REMOTE" != "git@github.com:$ORG_NAME/$REPO_NAME.git" ]; then
    echo "Warning: Existing remote 'origin' URL ($CURRENT_REMOTE) does not match the expected URL ($EXPECTED_REMOTE)."
    echo "Attempting to remove existing remote and add the correct one..."
    git remote remove origin
    if [ $? -ne 0 ]; then echo "Error: Failed to remove existing remote. Exiting."; exit 1; fi
    git remote add origin https://github.com/$ORG_NAME/$REPO_NAME
    if [ $? -ne 0 ]; then echo "Error: Failed to add correct remote after removal. Exiting."; exit 1; fi
    echo "Remote 'origin' updated."
  fi
fi


# Create the repository in the organization using gh CLI and push
# The --source=. flag is not used here because we are already in the directory and have committed.
# We just need to create the repo on GitHub and then push.
echo "Creating '$REPO_NAME' repo in '$ORG_NAME' with visibility '$VISIBILITY' on GitHub..."

# Use gh API to create the repo first, ignore error if it already exists
gh repo create "$ORG_NAME/$REPO_NAME" --"$VISIBILITY" --confirm --clone=false

# Check the exit status of the gh command
GH_EXIT_CODE=$?
if [ $GH_EXIT_CODE -eq 0 ]; then
    echo "Repository '$ORG_NAME/$REPO_NAME' created or already exists."
elif [ $GH_EXIT_CODE -ne 0 ]; then
    echo "Error: gh repo create failed with exit code $GH_EXIT_CODE. Ensure you are authenticated and have permissions."
    # You might want to check specific gh error messages here if needed
    exit 1
fi

# Push the local code to the remote repository
echo "Pushing local code to remote repository..."
git push -u origin master
if [ $? -ne 0 ]; then
    echo "Error: git push failed. Ensure the remote 'origin' is correct and you have push permissions."
    exit 1
fi

echo ""
echo "----------------------------------------------------"
echo "Process completed successfully!"
echo "Your project should now be available at https://github.com/$ORG_NAME/$REPO_NAME"
echo "----------------------------------------------------"
echo ""
echo "Note: If this is the very first time pushing after project creation,"
echo "you might see a message about setting the upstream branch."
echo "The '-u' flag in 'git push -u origin main' handles this."
echo ""
echo "To push future changes, simply run 'git push'."

"""