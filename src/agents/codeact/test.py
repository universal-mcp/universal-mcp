from agentr.agentr import Agentr
from agentr.client import AgentrRegistry
from agents.codeact import create_codeact
from agents.codeact.sandbox import eval_unsafe
from agents.llm import get_llm
from universal_mcp.tools import ToolManager
from universal_mcp.tools.adapters import ToolFormat

tool_manager = ToolManager()
tool_registry = AgentrRegistry()

model = get_llm("gpt-4.1")

agentr = Agentr()
agentr.load_tools(["google-mail_send_email"])

tools = agentr.list_tools(format=ToolFormat.NATIVE)

code_act = create_codeact(model, tools, eval_unsafe)
agent = code_act.compile()
