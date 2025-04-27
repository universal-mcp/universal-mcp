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

def generate_test_template(app_name: str) -> str:
    return """def test_dummy():
    assert True
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
    "universal-mcp>=0.1.12",
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
