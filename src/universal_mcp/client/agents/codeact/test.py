from universal_mcp.client.agents.codeact import create_codeact
from universal_mcp.client.agents.codeact.sandbox import eval_unsafe
from universal_mcp.client.agents.llm import get_llm
from universal_mcp.tools import ToolManager
from universal_mcp.tools.adapters import ToolFormat
from universal_mcp.utils.agentr import AgentrRegistry

tool_manager = ToolManager()
tool_registry = AgentrRegistry()

model = get_llm("gpt-4.1")

tool_manager = tool_registry.load_tools(["google-mail_send_email"], tool_manager)
tools = tool_manager.list_tools(format=ToolFormat.NATIVE)

code_act = create_codeact(model, tools, eval_unsafe)
agent = code_act.compile()
