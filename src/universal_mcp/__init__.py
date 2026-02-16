# Extend __path__ to enable namespace package behavior
# This allows universal_mcp.applications to be discovered from multiple packages
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

from universal_mcp.sdk import UniversalMCP

__version__ = "2.0.0"
__all__ = ["UniversalMCP", "__version__"]
