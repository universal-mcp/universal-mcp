import builtins
import contextlib
import io
from typing import Any

from universal_mcp.applications import app_from_slug
from universal_mcp.applications.sample_tool_app import SampleToolApp
from universal_mcp.client.agents.codeact import create_codeact
from universal_mcp.client.agents.llm import get_llm
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.tools import ToolManager
from universal_mcp.tools.adapters import ToolFormat

tool_manager = ToolManager()

sample_app = SampleToolApp()
gmail_app = app_from_slug("google-mail")
integration = AgentRIntegration(name="google-mail")
gmail_app_with_integration = gmail_app(integration)


tool_manager.register_tools_from_app(sample_app, tool_names=["get_simple_weather"])
tool_manager.register_tools_from_app(gmail_app_with_integration)


def eval(code: str, _locals: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    # Store original keys before execution
    original_keys = set(_locals.keys())
    result = f"Executing code...\n{code}\n\nOutput:\n"
    result += "=" * 50 + "\n"
    try:
        with contextlib.redirect_stdout(io.StringIO()) as f:
            # Execute the code in the provided locals context
            # Using exec to allow dynamic code execution
            # This is a simplified version; in production, consider security implications
            exec(code, builtins.__dict__, _locals)
        result += f.getvalue()
        if not result:
            result = "<code ran, no output printed to stdout>"
    except Exception as e:
        result += f"Error during execution: {repr(e)}"

    # Determine new variables created during execution
    new_keys = set(_locals.keys()) - original_keys
    new_vars = {key: _locals[key] for key in new_keys}
    return result, new_vars


tools = tool_manager.list_tools(format=ToolFormat.NATIVE)
# tools = [sample_app.get_simple_weather]


model = get_llm("gpt-4.1")

code_act = create_codeact(model, tools, eval)
agent = code_act.compile()

# response = agent.invoke()
# print(response)
