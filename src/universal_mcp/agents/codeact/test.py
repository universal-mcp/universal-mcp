from universal_mcp.agentr import Agentr
from universal_mcp.agents.codeact import create_codeact
from universal_mcp.agents.codeact.sandbox import eval_unsafe
from universal_mcp.agents.llm import get_llm
from universal_mcp.tools.adapters import ToolFormat

model = get_llm("gpt-4.1")

agentr = Agentr()
agentr.load_tools(["google-mail_send_email"])

tools = agentr.list_tools(format=ToolFormat.NATIVE)

code_act = create_codeact(model, tools, eval_unsafe)
agent = code_act.compile()
