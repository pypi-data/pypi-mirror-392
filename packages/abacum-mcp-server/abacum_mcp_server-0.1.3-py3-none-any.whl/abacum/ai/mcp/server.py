"""
Abacum MCP Server
Initializes the FastMCP server and provides the main entry point.
"""

from fastmcp import FastMCP
import sys
from .api import get_api_credentials, ApiError

# Initialize the MCP server
mcp = FastMCP("Abacum MCP Server")

# Import tools to register them
from . import tools

def main():
    """
    Main entry point for the MCP server.
    Validates credentials and runs the server with stdio.
    """
    try:
        # Validate credentials before starting
        get_api_credentials()
    except ApiError as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Run with stdio transport for Claude Desktop
    mcp.run()

if __name__ == "__main__":
    main()