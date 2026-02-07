"""
Sandbox implementations for isolated code execution.

Available sandbox types:
- InProcessSandbox: Fast in-process execution (default for code mode)
- SubprocessSandbox: Isolated subprocess execution for safer code running
"""

from universal_mcp.sandbox.sandbox import (
    DEFAULT_ERROR_HINT,
    ERROR_RECOVERY_HINTS,
    Sandbox,
    SandboxResult,
)
from universal_mcp.sandbox.in_process_sandbox import InProcessSandbox
from universal_mcp.sandbox.subprocess_sandbox import SubprocessSandbox

__all__ = [
    "Sandbox",
    "SandboxResult",
    "ERROR_RECOVERY_HINTS",
    "DEFAULT_ERROR_HINT",
    "InProcessSandbox",
    "SubprocessSandbox",
]
