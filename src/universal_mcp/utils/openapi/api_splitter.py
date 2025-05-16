import ast
import re
from collections import defaultdict
from keyword import iskeyword
from pathlib import Path

API_SEGMENT_BASE_CODE = '''
from typing import Any

class APISegmentBase:
    def __init__(self, main_app_client: Any):
        self.main_app_client = main_app_client

    def _get(self, url: str, params: dict = None, **kwargs):
        return self.main_app_client._get(url, params=params, **kwargs)

    def _post(self, url: str, data: Any = None, files: Any = None, params: dict = None, content_type: str = None, **kwargs):
        return self.main_app_client._post(url, data=data, files=files, params=params, content_type=content_type, **kwargs)

    def _put(self, url: str, data: Any = None, files: Any = None, params: dict = None, content_type: str = None, **kwargs):
        return self.main_app_client._put(url, data=data, files=files, params=params, content_type=content_type, **kwargs)

    def _patch(self, url: str, data: Any = None, params: dict = None, **kwargs):
        return self.main_app_client._patch(url, data=data, params=params, **kwargs)

    def _delete(self, url: str, params: dict = None, **kwargs):
        return self.main_app_client._delete(url, params=params, **kwargs)
'''

def get_sanitized_path_segment(openapi_path: str) -> str:
    # Remove leading/trailing slashes and split
    path_parts = [part for part in openapi_path.strip("/").split("/") if part]

    if not path_parts:
        return "default_api"

    # Handle common prefixes like /api/ or /v1/api/ etc.
    known_prefixes = ["api"] 
    while len(path_parts) > 0 and path_parts[0].lower() in known_prefixes:
        path_parts.pop(0)
        if not path_parts: 
            return "default_api" 

    segment_to_use = "default_api" 

    # check if the current first segment is version-like (e.g., "2", "v1", "v0")
    if path_parts:
        first_segment = path_parts[0]
        # Check if it's purely numeric (like "2") or matches "v" followed by digits
        is_version_segment = first_segment.isdigit() or re.match(r"v\\d+", first_segment.lower())

        if is_version_segment and len(path_parts) > 1:
            # If it's a version segment and there's something after it, use the next segment
            segment_to_use = path_parts[1]
        elif not is_version_segment:
            # If it's not a version segment, use it directly
            segment_to_use = path_parts[0]
        else:
      
            segment_to_use = f"api_{first_segment}"
    else: # Path was empty after stripping prefixes (e.g. "/api/")
        return "default_api" # segment_to_use remains "default_api"

    # Sanitize the chosen segment to be a valid Python identifier component
    # Replace non-alphanumeric (excluding underscore) with underscore
    sanitized_segment = re.sub(r"[^a-zA-Z0-9_]", "_", segment_to_use)
    
    # Remove leading/trailing underscores that might result from sanitization
    sanitized_segment = sanitized_segment.strip("_")

  
    if not sanitized_segment:
        return "default_api"
    if sanitized_segment.isdigit(): # e.g. if path was /2/123 -> segment is 123
        return f"api_{sanitized_segment}"
        
    return sanitized_segment

def get_group_name_from_path(openapi_path: str) -> str:
    processed_path = openapi_path
    
    # Pattern for /vN, /vN.N, /vN.N.N
    version_pattern_v_prefix = re.compile(r"^/v[0-9]+(?:\\.[0-9]+){0,2}")
    # Pattern for just /N (like /2)
    version_pattern_numeric_prefix = re.compile(r"^/[0-9]+")
    
    api_prefix_pattern = re.compile(r"^/api")

    # Strip /api prefix first if present
    if api_prefix_pattern.match(processed_path):
        processed_path = api_prefix_pattern.sub("", processed_path)
        processed_path = processed_path.lstrip("/") # Ensure we strip leading slash if api was the only thing
        if processed_path and not processed_path.startswith("/"):
             processed_path = "/" + processed_path
        elif not processed_path: # Path was only /api/
            processed_path = "/" # Reset to / so subsequent logic doesn't fail

    # Try to strip /vN style version
    path_after_v_version_strip = version_pattern_v_prefix.sub("", processed_path)
    
    if path_after_v_version_strip != processed_path: # /vN was stripped
        processed_path = path_after_v_version_strip
    else: # /vN was not found, try to strip /N (like /2/)
        path_after_numeric_version_strip = version_pattern_numeric_prefix.sub("", processed_path)
        if path_after_numeric_version_strip != processed_path: # /N was stripped
            processed_path = path_after_numeric_version_strip
            
    processed_path = processed_path.lstrip("/")

    path_segments = [segment for segment in processed_path.split("/") if segment] # Ensure no empty segments

    group_name_raw = "default"
    if path_segments and path_segments[0]:
        # Remove {param} style parts from the segment if any
        group_name_raw = re.sub(r"[{}]", "", path_segments[0]) # Corrected regex string
    
    # Sanitize to make it a valid Python identifier component (lowercase, underscores)
    group_name = re.sub(r"[^a-zA-Z0-9_]", "_", group_name_raw).lower() # Corrected regex string
    group_name = group_name.strip("_")

    if not group_name or group_name.isdigit(): # If empty after sanitization or purely numeric
        group_name = f"api_{group_name}" if group_name else "default_api"
    
    if iskeyword(group_name): # Avoid Python keywords
        group_name += "_"
        
    return group_name if group_name else "default_api"


class MethodTransformer(ast.NodeTransformer):
    def __init__(self, original_path: str):
        self.original_path = original_path

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        # All logic related to adding headers parameter has been removed.
        self.generic_visit(node)
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        if isinstance(node.value, ast.Name) and node.value.id == 'self' and node.attr == 'base_url':
            return ast.Attribute(
                value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='main_app_client', ctx=ast.Load()),
                attr='base_url',
                ctx=ast.Load()
            )
        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.Call:
        return self.generic_visit(node)


def split_generated_app_file(input_app_file: Path, output_dir: Path):
    content = input_app_file.read_text()
    tree = ast.parse(content)

    main_app_class_node = None
    for node_item in tree.body: # Renamed to avoid conflict with ast.Node
        if isinstance(node_item, ast.ClassDef) and \
           any(isinstance(base, ast.Name) and base.id == 'APIApplication' for base in node_item.bases if isinstance(base, ast.Name)):
            main_app_class_node = node_item
            break
    
    if not main_app_class_node:
        raise ValueError("Could not find main APIApplication class in the input file.")

    grouped_methods = defaultdict(list)
    other_main_app_body_nodes = []
    processed_method_names_in_main = set()
    
    openapi_path_regex = re.compile(r"# openapi_path: (.+)")

    for item in main_app_class_node.body:
        if isinstance(item, ast.FunctionDef):
            path_from_comment = None
            if item.body and isinstance(item.body[0], ast.Expr) and \
               isinstance(item.body[0].value, ast.Constant) and isinstance(item.body[0].value.value, str):
                docstring_lines = item.body[0].value.value.strip().splitlines()
                if docstring_lines:
                    match = openapi_path_regex.match(docstring_lines[0].strip())
                    if match:
                        path_from_comment = match.group(1).strip()
            
            if path_from_comment:
                group = get_group_name_from_path(path_from_comment)
                method_node_copy = ast.parse(ast.unparse(item)).body[0]
                if not isinstance(method_node_copy, ast.FunctionDef):
                     method_node_copy = item 

                transformer = MethodTransformer(original_path=path_from_comment)
                transformed_method_node = transformer.visit(method_node_copy)
                if hasattr(ast, 'fix_missing_locations'):
                    transformed_method_node = ast.fix_missing_locations(transformed_method_node)

                # Remove the # openapi_path: comment from the docstring
                if (transformed_method_node.body and
                        isinstance(transformed_method_node.body[0], ast.Expr) and
                        isinstance(transformed_method_node.body[0].value, ast.Constant) and
                        isinstance(transformed_method_node.body[0].value.value, str)):
                    
                    docstring_expr_node = transformed_method_node.body[0]
                    original_docstring_text = docstring_expr_node.value.value
                    
                    all_lines_raw = original_docstring_text.splitlines(True)
                    line_to_remove_idx = -1
                    
                    for i, current_line_raw in enumerate(all_lines_raw):
                        current_line_stripped = current_line_raw.strip()
                        if current_line_stripped: # Found the first significant line
                            if openapi_path_regex.match(current_line_stripped):
                                line_to_remove_idx = i
                            break # Only inspect the first significant line

                    if line_to_remove_idx != -1:
                        del all_lines_raw[line_to_remove_idx]
                        modified_docstring_text = "".join(all_lines_raw)
                        
                        if not modified_docstring_text.strip():
                            transformed_method_node.body.pop(0) # Docstring is now empty
                        else:
                            docstring_expr_node.value.value = modified_docstring_text
                
                grouped_methods[group].append(transformed_method_node)
                processed_method_names_in_main.add(item.name)
            else:
                other_main_app_body_nodes.append(item)
        else:
            other_main_app_body_nodes.append(item)
    
    # Define segments subfolder
    segments_foldername = "api_segments"
    segments_dir = output_dir / segments_foldername
    segments_dir.mkdir(parents=True, exist_ok=True)

    (segments_dir / "api_segment_base.py").write_text(API_SEGMENT_BASE_CODE)

    segment_class_details_for_main_app = []

    for group, method_nodes in grouped_methods.items():
        SegmentClassName = "".join(word.capitalize() for word in group.split("_")) + "Api"
        segment_filename = f"{group.lower()}_api.py"
        
        method_names_for_list_tools = [method_node.name for method_node in method_nodes]

        list_tools_body = [ast.Return(value=ast.List(
            elts=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr=name, ctx=ast.Load()) for name in method_names_for_list_tools],
            ctx=ast.Load()
        ))]
        list_tools_def = ast.FunctionDef(
            name='list_tools',
            args=ast.arguments(posonlyargs=[], args=[ast.arg(arg='self')], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
            body=list_tools_body, decorator_list=[], returns=None
        )
        
        init_method_segment = ast.FunctionDef(
            name='__init__',
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg='self'), ast.arg(arg='main_app_client', annotation=ast.Name(id='Any', ctx=ast.Load()))],
                vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
            ),
            body=[
                ast.Expr(value=ast.Call(
                    func=ast.Attribute(value=ast.Call(func=ast.Name(id='super', ctx=ast.Load()), args=[], keywords=[]), attr='__init__', ctx=ast.Load()),
                    args=[ast.Name(id='main_app_client', ctx=ast.Load())],
                    keywords=[]
                ))
            ],
            decorator_list=[], returns=None
        )

        segment_class_body = [init_method_segment] + method_nodes + [list_tools_def]
        segment_class_node = ast.ClassDef(
            name=SegmentClassName,
            bases=[ast.Name(id='APISegmentBase', ctx=ast.Load())],
            keywords=[], body=segment_class_body, decorator_list=[]
        )
        
        segment_module_body = [
            ast.ImportFrom(module='typing', names=[ast.alias(name='Any'), ast.alias(name='Dict'), ast.alias(name='Optional')], level=0),
            ast.ImportFrom(module='.api_segment_base', names=[ast.alias(name='APISegmentBase')], level=0), # This relative import is fine as they are in the same dir
            segment_class_node
        ]
        segment_module_ast = ast.Module(body=segment_module_body, type_ignores=[])
        if hasattr(ast, 'fix_missing_locations'):
            segment_module_ast = ast.fix_missing_locations(segment_module_ast)
            
        (segments_dir / segment_filename).write_text(ast.unparse(segment_module_ast))
        segment_class_details_for_main_app.append({
            "attr_name": group.lower(),
            "class_name": SegmentClassName,
            "module_name": segment_filename.replace(".py", "") # Used for import in main app
        })

    new_main_app_body = []
    main_app_init_node = None

    for node in other_main_app_body_nodes:
        if isinstance(node, ast.FunctionDef):
            if node.name == '__init__':
                main_app_init_node = node
                continue
            elif node.name == 'list_tools':
                continue
        new_main_app_body.append(node)

    if not main_app_init_node:
        main_app_init_node = ast.FunctionDef(
            name='__init__',
            args=ast.arguments(
                posonlyargs=[], 
                args=[ast.arg(arg='self'), ast.arg(arg='integration', annotation=ast.Name(id='Integration', ctx=ast.Load()), default=ast.Constant(value=None))],
                vararg=ast.arg(arg='args'), 
                kwonlyargs=[], kw_defaults=[], 
                kwarg=ast.arg(arg='kwargs'), 
                defaults=[ast.Constant(value=None)]
            ),
            body=[
                ast.Expr(value=ast.Call(
                    func=ast.Attribute(value=ast.Call(func=ast.Name(id='super', ctx=ast.Load()), args=[], keywords=[]), attr='__init__', ctx=ast.Load()),
                    args=[ast.keyword(arg='name', value=ast.Constant(value=main_app_class_node.name.lower())), ast.Name(id='integration', ctx=ast.Load())],
                    keywords=[ast.keyword(arg=None, value=ast.Name(id='kwargs',ctx=ast.Load()))]
                ))
            ],
            decorator_list=[], returns=ast.Constant(value=None)
        )

    init_segment_instantiations = []
    for seg_detail in segment_class_details_for_main_app:
        init_segment_instantiations.append(
            ast.Assign(
                targets=[ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr=seg_detail["attr_name"], ctx=ast.Store())],
                value=ast.Call(func=ast.Name(id=seg_detail["class_name"], ctx=ast.Load()), args=[ast.Name(id='self', ctx=ast.Load())], keywords=[])
            )
        )
    if not isinstance(main_app_init_node.body, list):
        main_app_init_node.body = [main_app_init_node.body] # type: ignore
        
    main_app_init_node.body.extend(init_segment_instantiations)
    new_main_app_body.insert(0, main_app_init_node)

    list_tools_calls_for_main = [
        ast.Call(
            func=ast.Attribute(value=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr=seg_detail["attr_name"], ctx=ast.Load()), attr='list_tools', ctx=ast.Load()),
            args=[], keywords=[]
        ) for seg_detail in segment_class_details_for_main_app
    ]
    
    new_list_tools_body = [ast.Assign(targets=[ast.Name(id='all_tools', ctx=ast.Store())], value=ast.List(elts=[], ctx=ast.Load()))]
    if list_tools_calls_for_main:
        for call_node in list_tools_calls_for_main:
            new_list_tools_body.append(ast.Expr(value=ast.Call(
                func=ast.Attribute(value=ast.Name(id='all_tools', ctx=ast.Load()), attr='extend', ctx=ast.Load()),
                args=[call_node], keywords=[]))
            )
    new_list_tools_body.append(ast.Return(value=ast.Name(id='all_tools', ctx=ast.Load())))

    new_main_app_list_tools_def = ast.FunctionDef(
        name='list_tools',
        args=ast.arguments(posonlyargs=[], args=[ast.arg(arg='self')], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=new_list_tools_body, decorator_list=[], returns=None
    )
    new_main_app_body.append(new_main_app_list_tools_def)

    main_app_class_node.body = new_main_app_body

    final_main_module_imports = []
    other_top_level_nodes_for_main = []
    original_imports_from_main_file = set()

    for top_node in tree.body:
        if top_node == main_app_class_node:
            continue
        if isinstance(top_node, ast.Import | ast.ImportFrom):
            final_main_module_imports.append(top_node)
            if isinstance(top_node, ast.ImportFrom):
                if top_node.module: # module can be None for from . import x
                     original_imports_from_main_file.add(top_node.module)
            elif isinstance(top_node, ast.Import):
                 for alias in top_node.names:
                      original_imports_from_main_file.add(alias.name)
        else:
            other_top_level_nodes_for_main.append(top_node)
            
    if "typing" not in original_imports_from_main_file:
         final_main_module_imports.insert(0, ast.ImportFrom(module='typing', names=[ast.alias(name='Any'), ast.alias(name='Dict'), ast.alias(name='Optional')], level=0))

    for seg_detail in segment_class_details_for_main_app:
        # Adjust import path for segments subfolder
        final_main_module_imports.append(
            ast.ImportFrom(module=f'.{segments_foldername}.{seg_detail["module_name"]}', names=[ast.alias(name=seg_detail["class_name"])], level=0)
        )
    
    final_main_app_module_ast = ast.Module(body=final_main_module_imports + other_top_level_nodes_for_main + [main_app_class_node], type_ignores=[])
    if hasattr(ast, 'fix_missing_locations'):
        final_main_app_module_ast = ast.fix_missing_locations(final_main_app_module_ast)

    (output_dir / "app.py").write_text(ast.unparse(final_main_app_module_ast))

    (output_dir / "__init__.py").touch(exist_ok=True)
    (segments_dir / "__init__.py").touch(exist_ok=True) 