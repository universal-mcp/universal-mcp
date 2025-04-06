import os
import ast
import base64
import importlib.util
import inspect
from pathlib import Path
import traceback
from typing import Optional

def echo(message: str, err: bool = False):
    """Echo a message to the console, with optional error flag."""
    print(message, file=os.sys.stderr if err else None)

async def generate_api_from_schema(
    schema_path: Path,
    output_path: Optional[Path] = None,
    add_docstrings: bool = True,
):
    """
    Generate API client from OpenAPI schema with optional docstring generation.
    
    Args:
        schema_path: Path to the OpenAPI schema file
        output_path: Output file path - should match the API name (e.g., 'twitter.py' for Twitter API)
        add_docstrings: Whether to add docstrings to the generated code
        
    Returns:
        dict: A dictionary with information about the generated files
    """
    if not schema_path.exists():
        echo(f"Error: Schema file {schema_path} does not exist", err=True)
        raise FileNotFoundError(f"Schema file {schema_path} does not exist")
    
    from universal_mcp.utils.openapi import generate_api_client, load_schema
    
    try:
        schema = load_schema(schema_path)
    except Exception as e:
        echo(f"Error loading schema: {e}", err=True)
        raise
    
    code = generate_api_client(schema)
    
    # If no output path is provided, just return the code
    if not output_path:
        return {"code": code}
    
    # Determine the folder name for the application
    folder_name = output_path.stem  # Get filename without extension
    
    # Create a temporary file for docstring processing
    temp_output_path = output_path
    
    # Save to file if output path is provided
    with open(temp_output_path, "w") as f:
        f.write(code)
    echo(f"Generated API client at: {temp_output_path}")
    
    # Verify the file was written correctly
    try:
        with open(temp_output_path, "r") as f:
            file_content = f.read()
            echo(f"Successfully wrote {len(file_content)} bytes to {temp_output_path}")
            
            # Basic syntax check
            try:
                ast.parse(file_content)
                echo("Python syntax check passed")
            except SyntaxError as e:
                echo(f"Warning: Generated file has syntax error: {e}", err=True)
    except Exception as e:
        echo(f"Error verifying output file: {e}", err=True)
    
    # Add docstrings if requested
    if add_docstrings:
        from universal_mcp.react_agent.graph import graph
        
        async def run_docstring():
            # Convert output_path to string if it's a Path object
            script_path = str(temp_output_path)
            echo(f"Adding docstrings to {script_path}...")
            
            # Debug: Check if the file exists
            if not os.path.exists(script_path):
                echo(f"Warning: File {script_path} does not exist", err=True)
                return None
            
            # Debug: Try reading the file
            try:
                with open(script_path, "r") as f:
                    content = f.read()
                    echo(f"Successfully read {len(content)} bytes from {script_path}")
            except Exception as e:
                echo(f"Error reading file for docstring generation: {e}", err=True)
                return None
            
            # Create input state with target_script_path
            input_state = {"target_script_path": script_path}
            echo(f"Passing input state: {input_state}")
            
            try:
                result = await graph.ainvoke(
                    input_state, 
                    {"recursion_limit": 100}
                )
                return result
            except Exception as e:
                echo(f"Error running docstring generation: {e}", err=True)
                traceback.print_exc()
                return None
        
        result = await run_docstring()
        
        if result:
            # Get the path to the file with docstrings (the _new file)
            output_dir = temp_output_path.parent
            file_name = temp_output_path.name
            file_name_without_ext, ext = os.path.splitext(file_name)
            new_file_path = output_dir / f"{file_name_without_ext}_new{ext}"
            
            if "functions_processed" in result:
                echo(f"Processed {result['functions_processed']} functions")
            
            if os.path.exists(new_file_path):
                echo(f"Temporary file with docstrings generated at: {new_file_path}")
                
                # Use the file with docstrings for the application
                source_file = new_file_path
            else:
                echo(f"Error: Expected output file {new_file_path} not found", err=True)
                # Fall back to the original file without docstrings
                source_file = temp_output_path
        else:
            echo("Docstring generation failed", err=True)
            # Fall back to the original file without docstrings
            source_file = temp_output_path
    else:
        # Use the original file without docstrings
        source_file = temp_output_path
        echo("Skipping docstring generation as requested")
        
        # Ensure new_file_path is defined even when skipping docstrings
        new_file_path = None
    
    # Now create the application folder structure regardless of docstring generation
    # Get the path to the applications directory
    applications_dir = Path(__file__).parent.parent / "applications"
    
    # Create a new directory for this application
    app_dir = applications_dir / folder_name
    app_dir.mkdir(exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    init_file = app_dir / "__init__.py"
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write("")
    
    # Copy the content to app.py in the new directory
    app_file = app_dir / "app.py"
    with open(source_file, "r") as src, open(app_file, "w") as dest:
        app_content = src.read()
        dest.write(app_content)
    
    echo(f"API client installed at: {app_file}")
    
    # Generate README.md file with function docs
    readme_file = None
    try:
        echo("Generating README.md from function information...")
        
        # Import the generated class and inspect it directly
        
        # Create a module spec and import the module
        spec = importlib.util.spec_from_file_location("temp_module", app_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the class in the module
        class_name = None
        class_obj = None
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == "temp_module":
                class_name = name
                class_obj = obj
                break
        
        if not class_name:
            class_name = folder_name.capitalize() + "App"
        
        # Find list_tools method to identify the tools
        tools = []
        
        # First attempt: Try to get tools from list_tools method
        if class_obj and hasattr(class_obj, 'list_tools'):
            # Create an instance of the class to call list_tools
            try:
                # Try to create an instance without arguments
                instance = class_obj()
                tool_list_func = getattr(instance, 'list_tools')
                tool_list = tool_list_func()
                
                # Extract function objects from the list
                for tool in tool_list:
                    func_name = tool.__name__
                    if func_name.startswith('_') or func_name in ('__init__', 'list_tools'):
                        continue
                    
                    # Get the docstring
                    doc = tool.__doc__ or f"Function for {func_name.replace('_', ' ')}"
                    # Get first paragraph as summary
                    summary = doc.split('\n\n')[0].strip()
                    tools.append((func_name, summary))
            except Exception as e:
                echo(f"Note: Couldn't instantiate class to get tool list: {e}")
        
        # Second attempt: If no tools found, look at all class methods
        if not tools and class_obj:
            for name, method in inspect.getmembers(class_obj, inspect.isfunction):
                if name.startswith('_') or name in ('__init__', 'list_tools'):
                    continue
                
                # Get the docstring
                doc = method.__doc__ or f"Function for {name.replace('_', ' ')}"
                # Get first paragraph as summary
                summary = doc.split('\n\n')[0].strip()
                tools.append((name, summary))
        
        # Generate content in HTML format that MarkitdownApp can convert
        html_content = f"<h1>{folder_name.replace('_', ' ').title()} Tool</h1>"
        html_content += f"<p>This is generated from openapi schema for the {folder_name.replace('_', ' ').title()} API.</p>"
        
        # Add Supported Integrations section (before Tool List)
        html_content += "<h2>Supported Integrations</h2>"
        html_content += "<p></p>"
        
        # Add Tools section with table format
        html_content += "<h2>Tool List</h2>"
        
        # Create a table for tools
        if tools:
            html_content += "<table>"
            html_content += "<tr><th>Tool</th><th>Description</th></tr>"
            
            for tool_name, tool_desc in tools:
                html_content += f"<tr><td>{tool_name}</td><td>{tool_desc}</td></tr>"
            
            html_content += "</table>"
        else:
            html_content += "<p>No tools with documentation were found in this API client.</p>"
        
        # Use MarkitdownApp to convert the HTML to markdown
        try:
            from universal_mcp.applications.markitdown.app import MarkitdownApp
            markitdown_app = MarkitdownApp()
            
            # Create a data URI with the HTML content
            encoded_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
            data_uri = f"data:text/html;base64,{encoded_html}"
            
            # Convert to markdown - handle the async function
            async def convert_async():
                return await markitdown_app.convert_to_markdown(data_uri)
            
            markdown_content = await convert_async()
            
            # Write README.md file
            readme_file = app_dir / "README.md"
            with open(readme_file, "w") as f:
                f.write(markdown_content)
            
            echo(f"Documentation generated at: {readme_file} using MarkitdownApp")
        except Exception as e:
            echo(f"Error using MarkitdownApp, falling back to direct markdown: {e}")
            
            # Fallback to direct markdown formatting if MarkitdownApp fails
            readme_content = f"# {folder_name.replace('_', ' ').title()} Tool\n\n"
            readme_content += f"This is automatically generated from openapi schema for the {folder_name.replace('_', ' ').title()} API.\n\n"
            
            # Add Supported Integrations section (before Tool List)
            readme_content += "## Supported Integrations\n\n"
            readme_content += "\n\n"
            
            # Add Tools section with table format
            readme_content += "## Tool List\n\n"
            
            if tools:
                # Create markdown table for tools
                readme_content += "| Tool | Description |\n"
                readme_content += "|------|-------------|\n"
                
                for tool_name, tool_desc in tools:
                    readme_content += f"| {tool_name} | {tool_desc} |\n"
                
                readme_content += "\n"
            else:
                readme_content += "No tools with documentation were found in this API client.\n\n"
            
            # Write README.md file as direct markdown
            readme_file = app_dir / "README.md"
            with open(readme_file, "w") as f:
                f.write(readme_content)
            
            echo(f"Documentation generated at: {readme_file} using direct markdown")
            
    except Exception as e:
        echo(f"Warning: Failed to generate README.md: {e}", err=True)
        traceback.print_exc()
    
    # Clean up temporary files if needed
    if os.path.exists(temp_output_path):
        os.remove(temp_output_path)
        echo(f"Temporary file {temp_output_path} removed")
    
    if new_file_path and os.path.exists(new_file_path) and new_file_path != temp_output_path:
        os.remove(new_file_path)
        echo(f"Temporary file {new_file_path} removed")
    
    return {
        "app_file": str(app_file),
        "readme_file": str(readme_file) if readme_file else None,
        "folder_name": folder_name,
        "class_name": class_name if 'class_name' in locals() else None,
        "tools": tools if 'tools' in locals() else []
    } 