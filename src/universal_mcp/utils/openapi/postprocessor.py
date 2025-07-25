import ast
from pathlib import Path
import re

def add_hint_tags_to_docstrings(input_path: str, output_path: str):
    """
    Reads a Python API client file, inspects each function, and adds a tag to the docstring:
    - 'readOnlyHint' for GET/POST/PUT
    - 'destructiveHint' for DELETE
    Does not alter other tags in the docstring.
    Writes the modified code to output_path.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        source = f.read()
    tree = ast.parse(source)
    
    class DocstringTagAdder(ast.NodeTransformer):
        def _find_http_method(self, node):
            """Find the HTTP method used in the function body."""
            http_methods = []
            
            def visit_node(n):
                if isinstance(n, ast.Call):
                    if isinstance(n.func, ast.Attribute):
                        if isinstance(n.func.value, ast.Name) and n.func.value.id == 'self':
                            method_name = n.func.attr
                            if method_name in ['_get', '_post', '_put', '_patch', '_delete']:
                                http_methods.append(method_name[1:]) 
                for child in ast.iter_child_nodes(n):
                    visit_node(child)
            
            visit_node(node)
            return http_methods[0] if http_methods else None
        
        def visit_FunctionDef(self, node):
            http_method = self._find_http_method(node)
            tag_to_add = None
            
            if http_method in ['get', 'post', 'put', 'patch']:
                tag_to_add = 'readOnlyHint'
            elif http_method == 'delete':
                tag_to_add = 'destructiveHint'
            
            if tag_to_add:
                docstring = ast.get_docstring(node, clean=False)
                if docstring is not None:
                    # Look for Tags: section in the docstring
                    tags_match = re.search(r'Tags:\s*(.+)', docstring, re.DOTALL)
                    if tags_match:
                        tags_line = tags_match.group(1).strip()
                        # Parse existing tags
                        existing_tags = [tag.strip() for tag in tags_line.split(',')]
                        if tag_to_add not in existing_tags:
                            # Add the new tag to the existing list
                            new_tags_line = tags_line.rstrip() + f", {tag_to_add}"
                            new_docstring = re.sub(
                                r'(Tags:\s*)(.+)',
                                r'\1' + new_tags_line,
                                docstring,
                                flags=re.DOTALL
                            )
                            # Replace docstring
                            if isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                                node.body[0].value.value = new_docstring
            return node
    
    new_tree = DocstringTagAdder().visit(tree)
    ast.fix_missing_locations(new_tree)
    new_source = ast.unparse(new_tree)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_source)
