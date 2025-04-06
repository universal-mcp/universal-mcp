"""Default prompts used by the agent."""

SYSTEM_PROMPT = """You are a helpful AI assistant specialized in writing high-quality Google-style Python docstrings.
"""

DOCSTRING_PROMPT = """Generate a high-quality Google-style docstring for the following Python function. 
Analyze the function's name, parameters, return values, and functionality to create a comprehensive docstring.

The docstring should:
1. Start with a clear, concise summary of what the function does
2. Include Args section with description of each parameter
3. Include Returns section describing the return value
4. Be formatted according to Google Python Style Guide

Here is the function:

{function_code}

Respond with the docstring only, without any additional explanation or markdown formatting.
"""