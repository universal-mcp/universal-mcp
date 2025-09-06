import json

from langchain_mcp_adapters.client import MultiServerMCPClient

from universal_mcp.agentr.integration import AgentrIntegration
from universal_mcp.applications.utils import app_from_slug
from universal_mcp.tools.adapters import ToolFormat
from universal_mcp.tools.manager import ToolManager
from universal_mcp.types import ToolConfig


async def load_agentr_tools(agentr_servers: dict):
    tool_manager = ToolManager()
    for app_name, tool_names in agentr_servers.items():
        app = app_from_slug(app_name)
        integration = AgentrIntegration(name=app_name)
        app_instance = app(integration=integration)
        tool_manager.register_tools_from_app(app_instance, tool_names=tool_names["tools"])
    tools = tool_manager.list_tools(format=ToolFormat.LANGCHAIN)
    return tools


async def load_mcp_tools(mcp_servers: dict):
    client = MultiServerMCPClient(mcp_servers)
    tools = await client.get_tools()
    return tools


async def load_tools(path: str) -> ToolConfig:
    with open(path) as f:
        data = json.load(f)
        config = ToolConfig.model_validate(data)
        agentr_tools = await load_agentr_tools(config.model_dump(exclude_none=True)["agentrServers"])
        mcp_tools = await load_mcp_tools(config.model_dump(exclude_none=True)["mcpServers"])
        return agentr_tools + mcp_tools
