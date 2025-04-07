"""Main entry point for the universal_mcp package when run as a module."""

import sys
from universal_mcp.cli import app

if __name__ == "__main__":
    sys.exit(app()) 