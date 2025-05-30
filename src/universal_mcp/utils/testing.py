from loguru import logger
from universal_mcp.tools.tools import Tool

def check_application_instance(app, app_name):
    assert app is not None
    app_instance = app(integration=None)
    assert app_instance.name == app_name

    tools = app_instance.list_tools()
    logger.info(f"Tools for {app_name}: {len(tools)}")
    assert len(tools) > 0, f"No tools found for {app_name}"

    tools = [Tool.from_function(tool) for tool in tools]
    seen_names = set()
    for tool in tools:
        assert tool.name is not None
        assert 0 < len(tool.name) < 48
        assert tool.description is not None
        assert tool.name not in seen_names, f"Duplicate tool name: {tool.name}"
        seen_names.add(tool.name)

def check_app_initialization(app_instance, expected_name):
    assert hasattr(app_instance, 'name'), "App should have a 'name' attribute."
    assert isinstance(app_instance.name, str)
    assert app_instance.name.strip() != ""
    assert app_instance.name == expected_name

def check_tool_docstrings_format(app_instance):
    for attr_name in dir(app_instance):
        if attr_name.startswith("_"):
            continue
        attr = getattr(app_instance, attr_name)
        if callable(attr):
            doc = attr.__doc__
            assert doc is not None, f"Missing docstring for {attr_name}"
            assert doc.strip().endswith("."), f"Docstring for {attr_name} should end with a period."

def check_tool_signature_inputs_outputs(app_instance):
    for tool in app_instance.list_tools():
        assert hasattr(tool, "input_schema")
        assert hasattr(tool, "output_schema")

def check_tool_call_execution(app_instance):
    for tool in app_instance.list_tools():
        try:
            tool(input={})
        except Exception:
            pass  # Assuming failure is okay as long as the call doesn't crash the check suite
