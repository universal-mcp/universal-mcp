import os
from typing import Literal
import ast
import re
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.types import Command
import asyncio

# Check the paths
from universal_mcp.react_agent.configuration import Configuration
from universal_mcp.react_agent.prompts import SYSTEM_PROMPT, DOCSTRING_PROMPT
from universal_mcp.react_agent.state import DocstringOutput, InputState, OutputState, State
from universal_mcp.react_agent.utils import load_chat_model, extract_functions_from_script

async def init_node(state: State, config: RunnableConfig) -> Command[Literal["llm_node"]]:
    """Initialize the agent state with extracted functions from the target script.
    
    Args:
        state: The current state of the agent
        config: Configuration for the runnable
        
    Returns:
        Command directing to the next node
    """
    # Get configuration - not used but kept for consistency with other nodes
    # configuration = Configuration.from_runnable_config(config)
    
    # Extract the target script path from the configuration
    target_script_path = state.get("target_script_path")
    
    if not target_script_path:
        raise ValueError("No target script path provided. Make sure to pass 'target_script_path' in the input state.")
    
    print(f"Processing script: {target_script_path}")
    
    # Check if file exists
    if not os.path.exists(target_script_path):
        raise FileNotFoundError(f"Script file not found: {target_script_path}")
    
    try:
        # Read the original script asynchronously
        original_script = await asyncio.to_thread(lambda: open(target_script_path, "r").read())
        
        # Extract functions asynchronously
        extracted_functions = await asyncio.to_thread(extract_functions_from_script, target_script_path)
        
        print(f"Extracted {len(extracted_functions)} functions from {target_script_path}")
        
        return Command(
            update={
                "extracted_functions": extracted_functions,
                "original_script": original_script,
                "current_function_index": 0,
                "docstrings": {},
                "target_script_path": target_script_path  # Store it in the state for later use
            },
            goto="llm_node"
        )
    except Exception as e:
        print(f"Error initializing docstring generation: {e}")
        raise
    
async def llm_node(state: State, config: RunnableConfig) -> Command[Literal["tool_node", "__end__"]]:
    """Generate a docstring for the current function using an LLM with structured output.
    
    Args:
        state: The current state of the agent
        config: Configuration for the runnable
        
    Returns:
        Command directing to the next node or ending the workflow
    """
    # Get configuration
    configuration = Configuration.from_runnable_config(config)
    
    # Check if we've processed all functions
    if state["current_function_index"] >= len(state["extracted_functions"]):
        return Command(
            update={},
            goto="__end__"
        )
    
    function_name, function_code = state["extracted_functions"][state["current_function_index"]]
    chat_model = load_chat_model(configuration.model)
    system_message = SystemMessage(content=SYSTEM_PROMPT.format())
    human_message = HumanMessage(content=DOCSTRING_PROMPT.format(function_code=function_code))
    structured_model = chat_model.with_structured_output(DocstringOutput)
    docstring_response = await structured_model.ainvoke([system_message, human_message])
    formatted_docstring = f"{docstring_response.summary}\n\n"
    
    if docstring_response.args:
        formatted_docstring += "Args:\n"
        for arg_name, arg_desc in docstring_response.args.items():
            formatted_docstring += f"    {arg_name}: {arg_desc}\n"
        formatted_docstring += "\n"
    
    if docstring_response.returns:
        formatted_docstring += f"Returns:\n    {docstring_response.returns}\n\n"
    
    docstrings = state.get("docstrings", {})
    docstrings[function_name] = formatted_docstring.strip()
    
    return Command(
        update={
            "docstrings": docstrings,
            "current_function_index": state["current_function_index"] + 1
        },
        goto="tool_node"
    )
    
async def tool_node(state: State, config: RunnableConfig) -> Command[Literal["llm_node", "__end__"]]:
    """Add the generated docstring to the function and update the script.
    
    Args:
        state: The current state of the agent
        config: Configuration for the runnable
        
    Returns:
        Command directing to the next node
    """
    # Process the current function
    current_index = state["current_function_index"] - 1  # The index we just processed
    
    # Safety check for empty extracted_functions
    if not state.get("extracted_functions"):
        print("Warning: No functions were extracted from the script")
        return Command(
            update={
                "functions_processed": 0
            },
            goto="__end__"
        )
    
    # Check if current_index is valid
    if current_index < 0 or current_index >= len(state["extracted_functions"]):
        print(f"Warning: Invalid function index {current_index} (total functions: {len(state['extracted_functions'])})")
        return Command(
            update={
                "functions_processed": state.get("functions_processed", 0)
            },
            goto="__end__"
        )
    
    function_name, function_code = state["extracted_functions"][current_index]
    docstring = state["docstrings"].get(function_name, "")
    
    print(f"Processing function: {function_name}")
    
    if not docstring:
        print(f"Warning: No docstring generated for function {function_name}")
        return Command(
            update={},
            goto="llm_node"
        )
    
    updated_script = state["original_script"] 
    function_position = updated_script.find(function_code)
    
    if function_position == -1:
        print(f"Warning: Could not find function {function_name} in the script")
        return Command(
            update={},
            goto="llm_node"
        )
    
    try:
        function_ast = ast.parse(function_code)
        if function_ast.body and hasattr(function_ast.body[0], 'body'):
            # Check if the function already has a docstring
            first_element = function_ast.body[0].body[0] if function_ast.body[0].body else None
            has_docstring = (isinstance(first_element, ast.Expr) and 
                            isinstance(first_element.value, ast.Constant) and 
                            isinstance(first_element.value.value, str))
            
            if has_docstring:
                print(f"Function {function_name} already has a docstring, will replace it")
            
            # Get the function definition line
            function_def_lines = function_code.split('\n', 1)
            function_def = function_def_lines[0]
            
            # If the function has a multi-line definition, find the end of the definition
            if not function_def.strip().endswith(':'):
                for i, line in enumerate(function_code.splitlines()):
                    if line.strip().endswith(':'):
                        function_def = '\n'.join(function_code.splitlines()[:i+1])
                        break
            
            # After function definition, before function body
            function_code_parts = function_code.split(function_def, 1)
            if len(function_code_parts) > 1:
                function_body = function_code_parts[1]
                
                # If the function already has a docstring, remove it
                if has_docstring:
                    # Try to find the end of the existing docstring
                    docstring_start = function_body.find('"""')
                    if docstring_start >= 0:
                        docstring_end = function_body.find('"""', docstring_start + 3)
                        if docstring_end >= 0:
                            # Remove the existing docstring
                            function_body = function_body[docstring_end + 3:]
                
                function_lines = function_code.splitlines()
                function_def_line = None
                function_body_start_line = None

                for i, line in enumerate(function_lines):
                    if re.match(r'\s*def\s+', line) and line.strip().endswith(':'):
                        function_def_line = i
                    elif function_def_line is not None and line.strip() and not line.strip().startswith('@'):
                        function_body_start_line = i
                        break

                if function_def_line is not None and function_body_start_line is not None:
                    # Get the indentation of the function body
                    body_line = function_lines[function_body_start_line]
                    body_indent = ' ' * (len(body_line) - len(body_line.lstrip()))
                    
                    docstring_lines = docstring.split('\n')
                    indented_docstring = []
                    
                    indented_docstring.append(f"{body_indent}\"\"\"")
                    
                    for line in docstring_lines:
                        if line.strip():
                            indented_docstring.append(f"{body_indent}{line}")
                        else:
                            indented_docstring.append(f"{body_indent}")
                    
                    indented_docstring.append(f"{body_indent}\"\"\"")
                    
                    formatted_docstring = '\n'.join(indented_docstring)
                    
                    updated_function = function_def + '\n' + formatted_docstring + function_body
                    
                    # Replace the function in the script
                    old_script = updated_script
                    updated_script = updated_script.replace(function_code, updated_function)
                    
                    # Check if replacement was successful
                    if old_script == updated_script:
                        print(f"Warning: Failed to update function {function_name} in the script")
                    else:
                        print(f"Successfully added docstring to function {function_name}")
    except Exception as e:
        print(f"Error processing function {function_name}: {e}")
        import traceback
        traceback.print_exc()
    
    is_last_function = state["current_function_index"] >= len(state["extracted_functions"])
    
    if is_last_function:
        print("Finished processing all functions")
        
        target_script_path = state.get("target_script_path")
        
        if not target_script_path:
            raise ValueError("No target script path provided")
        
        file_dir = os.path.dirname(target_script_path)
        file_name = os.path.basename(target_script_path)
        file_name_without_ext, ext = os.path.splitext(file_name)
        new_file_name = f"{file_name_without_ext}_new{ext}"
        new_file_path = os.path.join(file_dir, new_file_name)
        
        print(f"Writing docstring-enhanced script to: {new_file_path}")
        
        # Save the updated script asynchronously
        async def write_file_async(path, content):
            try:
                await asyncio.to_thread(lambda: open(path, "w").write(content))
                print(f"Successfully wrote {len(content)} bytes to {path}")
            except Exception as e:
                print(f"Error writing to {path}: {e}")
                raise

        await write_file_async(new_file_path, updated_script)
    
    return Command(
        update={
            "original_script": updated_script,
            "functions_processed": state.get("functions_processed", 0) + 1
        },
        goto="llm_node" if not is_last_function else "__end__"
    )
# Create the workflow graph
workflow = StateGraph(State, input=InputState, output=OutputState, config_schema=Configuration)
workflow.add_node("init_node", init_node)
workflow.add_node("llm_node", llm_node)
workflow.add_node("tool_node", tool_node)
workflow.add_edge("__start__", "init_node")

graph = workflow.compile()
graph.name = "docstring"  # This customizes the name in LangSmith