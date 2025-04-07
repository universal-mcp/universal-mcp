import os
import ast
import base64
import importlib.util
import inspect
import json
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

from universal_mcp.utils.openapi import generate_api_client, load_schema
from universal_mcp.utils.docgen import process_file

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
    try:
        # Validate schema file existence
        if not schema_path.exists():
            echo(f"Error: Schema file {schema_path} does not exist", err=True)
            raise FileNotFoundError(f"Schema file {schema_path} does not exist")
        
        # Load and parse the OpenAPI schema
        try:
            schema = load_schema(schema_path)
        except Exception as e:
            echo(f"Error loading schema: {e}", err=True)
            raise
        
        # Generate API client code from schema
        code = generate_api_client(schema)
        
        # Return generated code if no output path specified
        if not output_path:
            return {"code": code}
        
        folder_name = output_path.stem
        temp_output_path = output_path
        
        # Write generated code to file
        with open(temp_output_path, "w") as f:
            f.write(code)
        echo(f"Generated API client at: {temp_output_path}")
        
        # Verify file contents and perform syntax check
        try:
            with open(temp_output_path, "r") as f:
                file_content = f.read()
                echo(f"Successfully wrote {len(file_content)} bytes to {temp_output_path}")
                
                try:
                    ast.parse(file_content)
                    echo("Python syntax check passed")
                except SyntaxError as e:
                    echo(f"Warning: Generated file has syntax error: {e}", err=True)
        except Exception as e:
            echo(f"Error verifying output file: {e}", err=True)
        
        # Handle docstring generation if enabled
        if add_docstrings:
            async def run_docstring():
                script_path = str(temp_output_path)
                echo(f"Adding docstrings to {script_path}...")
                
                # Verify file existence before processing
                if not os.path.exists(script_path):
                    echo(f"Warning: File {script_path} does not exist", err=True)
                    return {"functions_processed": 0}
                
                # Read file content for docstring processing
                try:
                    with open(script_path, "r") as f:
                        content = f.read()
                        echo(f"Successfully read {len(content)} bytes from {script_path}")
                except Exception as e:
                    echo(f"Error reading file for docstring generation: {e}", err=True)
                    return {"functions_processed": 0}
                
                # Process file to add docstrings
                try:
                    processed = process_file(script_path)
                    return {"functions_processed": processed}
                except Exception as e:
                    echo(f"Error running docstring generation: {e}", err=True)
                    traceback.print_exc()
                    return {"functions_processed": 0}
            
            # Execute docstring generation
            result = await run_docstring()
            
            if result:
                if "functions_processed" in result:
                    echo(f"Processed {result['functions_processed']} functions")
                source_file = temp_output_path
            else:
                echo("Docstring generation failed", err=True)
                source_file = temp_output_path
        else:
            source_file = temp_output_path
            echo("Skipping docstring generation as requested")
        
        # Set up application directory structure
        applications_dir = Path(__file__).parent.parent / "applications"
        app_dir = applications_dir / folder_name
        app_dir.mkdir(exist_ok=True)
        
        # Create __init__.py for Python package
        init_file = app_dir / "__init__.py"
        if not init_file.exists():
            with open(init_file, "w") as f:
                f.write("")
        
        # Copy generated code to final location
        app_file = app_dir / "app.py"
        with open(source_file, "r") as src, open(app_file, "w") as dest:
            app_content = src.read()
            dest.write(app_content)
        
        echo(f"API client installed at: {app_file}")
        
        # Generate README.md with API documentation
        readme_file = None
        try:
            echo("Generating README.md from function information...")
            
            # Import generated module for inspection
            spec = importlib.util.spec_from_file_location("temp_module", app_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the main class in the generated module
            class_name = None
            class_obj = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and obj.__module__ == "temp_module":
                    class_name = name
                    class_obj = obj
                    break
            
            if not class_name:
                class_name = folder_name.capitalize() + "App"
            
            # Collect tool information from the class
            tools = []
            
            # Method 1: Try to get tools from list_tools method
            if class_obj and hasattr(class_obj, 'list_tools'):
                try:
                    instance = class_obj()
                    tool_list_func = getattr(instance, 'list_tools')
                    tool_list = tool_list_func()
                    
                    for tool in tool_list:
                        func_name = tool.__name__
                        if func_name.startswith('_') or func_name in ('__init__', 'list_tools'):
                            continue
                        
                        doc = tool.__doc__ or f"Function for {func_name.replace('_', ' ')}"
                        summary = doc.split('\n\n')[0].strip()
                        tools.append((func_name, summary))
                except Exception as e:
                    echo(f"Note: Couldn't instantiate class to get tool list: {e}")
            
            # Method 2: Fall back to inspecting class methods directly
            if not tools and class_obj:
                for name, method in inspect.getmembers(class_obj, inspect.isfunction):
                    if name.startswith('_') or name in ('__init__', 'list_tools'):
                        continue
                    
                    doc = method.__doc__ or f"Function for {name.replace('_', ' ')}"
                    summary = doc.split('\n\n')[0].strip()
                    tools.append((name, summary))
            
            # Generate README content
            readme_content = f"# {folder_name.replace('_', ' ').title()} Tool\n\n"
            readme_content += f"This is automatically generated from OpenAPI schema for the {folder_name.replace('_', ' ').title()} API.\n\n"
            
            readme_content += "## Supported Integrations\n\n"
            readme_content += "This tool can be integrated with any service that supports HTTP requests.\n\n"
            
            readme_content += "## Tool List\n\n"
            
            if tools:
                readme_content += "| Tool | Description |\n"
                readme_content += "|------|-------------|\n"
                
                for tool_name, tool_desc in tools:
                    readme_content += f"| {tool_name} | {tool_desc} |\n"
                
                readme_content += "\n"
            else:
                readme_content += "No tools with documentation were found in this API client.\n\n"
            
            # Write README file
            readme_file = app_dir / "README.md"
            with open(readme_file, "w") as f:
                f.write(readme_content)
            
            echo(f"Documentation generated at: {readme_file}")
        except Exception as e:
            echo(f"Error generating documentation: {e}", err=True)
        
        return {
            "app_file": str(app_file),
            "readme_file": str(readme_file) if readme_file else None
        }
        
    finally:
        # Clean up temporary file
        if output_path and output_path.exists():
            try:
                output_path.unlink()
                echo(f"Cleaned up temporary file: {output_path}")
            except Exception as e:
                echo(f"Warning: Could not remove temporary file {output_path}: {e}", err=True) 