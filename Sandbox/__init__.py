"""
Sandbox implementations for isolated code execution.

Available sandbox types:
- InProcessSandbox: Fast in-process execution for development
- SubprocessSandbox: Isolated subprocess execution for safer code running
- E2BSandbox: Cloud-based E2B sandbox for production
"""

from universal_mcp.agents.Sandbox.e2b_sandbox import E2BSandbox
from universal_mcp.agents.Sandbox.in_process_sandbox import InProcessSandbox
from universal_mcp.agents.Sandbox.sandbox import (
    DEFAULT_ERROR_HINT,
    ERROR_RECOVERY_HINTS,
    Sandbox,
    SandboxResult,
)
from universal_mcp.agents.Sandbox.subprocess_sandbox import SubprocessSandbox

__all__ = [
    "Sandbox",
    "SandboxResult",
    "ERROR_RECOVERY_HINTS",
    "DEFAULT_ERROR_HINT",
    "InProcessSandbox",
    "SubprocessSandbox",
    "E2BSandbox",
]
