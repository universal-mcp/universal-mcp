import ast
import re

import litellm


def add_hint_tags_to_docstrings(input_path: str, output_path: str):
    """
    Reads a Python API client file, inspects each function, and adds a tag to the docstring:
    - 'readOnlyHint' for GET/POST/PUT
    - 'destructiveHint' for DELETE
    Does not alter other tags in the docstring.
    Writes the modified code to output_path.
    """
    with open(input_path, encoding='utf-8') as f:
        source = f.read()
    tree = ast.parse(source)
    
    # Initialize counters
    total_functions = 0
    functions_with_http_methods = 0
    functions_processed_by_llm = 0
    functions_tagged = 0
    llm_failures = 0
    
    class DocstringTagAdder(ast.NodeTransformer):
        def _find_http_method(self, node):
            """Find the HTTP method used in the function body."""
            http_methods = []
            
            def visit_node(n):
                if (isinstance(n, ast.Call) and 
                    isinstance(n.func, ast.Attribute) and
                    isinstance(n.func.value, ast.Name) and 
                    n.func.value.id == 'self' and
                    n.func.attr in ['_get', '_post', '_put', '_patch', '_delete']):
                    http_methods.append(n.func.attr[1:]) 
                for child in ast.iter_child_nodes(n):
                    visit_node(child)
            
            visit_node(node)
            return http_methods[0] if http_methods else None
        
        def visit_FunctionDef(self, node):
            nonlocal total_functions, functions_with_http_methods, functions_processed_by_llm, functions_tagged, llm_failures
            
            total_functions += 1
            print(f"\n[{total_functions}] Processing function: {node.name}")
            
            http_method = self._find_http_method(node)
            tag_to_add = None
            
            if http_method:
                functions_with_http_methods += 1
                print(f"  └─ Found HTTP method: {http_method.upper()}")
                
                # Use simple agent to decide tag
                print("  └─ Calling LLM to determine tag...")
                tag_to_add = self._get_tag_suggestion_from_agent(node, http_method)
                
                if tag_to_add:
                    functions_processed_by_llm += 1
                    print(f"  └─ LLM suggested tag: {tag_to_add}")
                else:
                    print("  └─ LLM failed or returned invalid response")
            else:
                print("  └─ No HTTP method found - skipping")
            
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
                                functions_tagged += 1
                                print(f"  └─ ✅ Tag '{tag_to_add}' added successfully")
                        else:
                            print(f"  └─ ⚠️  Tag '{tag_to_add}' already exists - skipping")
                    else:
                        print("  └─ ⚠️  No 'Tags:' section found in docstring - skipping")
                else:
                    print("  └─ ⚠️  No docstring found - skipping")
            return node
        
        def _get_tag_suggestion_from_agent(self, node, http_method):
            """Use a simple agent to decide which tag to add based on function context."""
            
            function_name = node.name
            docstring = ast.get_docstring(node, clean=False) or ""
            parameters = [arg.arg for arg in node.args.args if arg.arg != 'self']
            
            system_prompt = """You are an expert at analyzing API functions and determining their safety level.
            
            Your task is to analyze each function and decide which tag to add:
            - 'readOnlyHint': for functions that are safe, read-only, or non-destructive
            - 'destructiveHint': for functions that modify data, delete resources, or are potentially dangerous
            
            Think through the function's purpose, HTTP method, parameters, and docstring to make your decision.
            
            Respond with ONLY one word: either 'readOnlyHint' or 'destructiveHint'"""
            
            user_prompt = f"""Analyze this API function and decide which tag to add:

Function Name: {function_name}
HTTP Method: {http_method}
Parameters: {', '.join(parameters)}
Docstring: {docstring[:1000]}...


Based on this information, should this function get 'readOnlyHint' or 'destructiveHint'?

Think through:
1. What does this function do? (from name and docstring)
2. Is it modifying/deleting data or just reading?
3. Could it be potentially dangerous or destructive
            # Example: Not all PUT or POST methods are destructive.
            # For example, a "like" function may use PUT to register a like, but this is not truly destructive.
            # Similarly, sometimes a POST request is used to fetch or search for something, not to modify data.


Your answer (one word only):"""
            
            try:
                response = litellm.completion(
                    model="perplexity/sonar",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=10
                )
                
                suggested_tag = response.choices[0].message.content.strip().lower()
                
                if suggested_tag in ['readonlyhint', 'destructivehint']:
                    return 'readOnlyHint' if suggested_tag == 'readonlyhint' else 'destructiveHint'
                else:
                    # If LLM gives unexpected response, return None (no tag added)
                    return None
                        
            except Exception as e:
                nonlocal llm_failures
                llm_failures += 1
                print(f"  └─ ❌ LLM failed for function {function_name}: {e}")
                # If LLM fails, return None (no tag added)
                return None
    
    new_tree = DocstringTagAdder().visit(tree)
    ast.fix_missing_locations(new_tree)
    new_source = ast.unparse(new_tree)
    
    # Print summary statistics
    print(f"\n{'='*60}")
    print("📊 PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total functions processed: {total_functions}")
    print(f"Functions with HTTP methods: {functions_with_http_methods}")
    print(f"Functions processed by LLM: {functions_processed_by_llm}")
    print(f"Functions successfully tagged: {functions_tagged}")
    print(f"LLM failures: {llm_failures}")
    print(f"Success rate: {(functions_tagged/total_functions*100):.1f}% of all functions")
    if functions_with_http_methods > 0:
        print(f"LLM success rate: {(functions_processed_by_llm/functions_with_http_methods*100):.1f}% of HTTP functions")
    print(f"{'='*60}")
    
    # Format with Black in memory
    try:
        import black
        formatted_content = black.format_file_contents(new_source, fast=False, mode=black.FileMode())
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        print(f"Black formatting applied successfully to: {output_path}")
    except ImportError:
        print(f"Black not installed. Skipping formatting for: {output_path}")
        # Write unformatted version if Black is not available
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_source)
    except Exception as e:
        print(f"Black formatting failed for {output_path}: {e}")
        # Write unformatted version if Black formatting fails
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_source)
