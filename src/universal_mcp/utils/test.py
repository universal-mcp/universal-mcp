import importlib.util
from pathlib import Path

from universal_mcp.utils.api_generator import collect_tools, generate_readme

app_dir = Path("src/universal_mcp/applications/e2b")
app_file = app_dir / "app.py"

spec = importlib.util.spec_from_file_location("e2b_module", app_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class_obj = module.E2BApp

tools = collect_tools(class_obj, "e2b")

readme_file = generate_readme(app_dir, "e2b", tools)
print(f"README generated at: {readme_file}")

