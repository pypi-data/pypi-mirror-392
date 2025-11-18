"""MusicMCP.AI MCP Server package."""
from .api import mcp


def main():
    """MCP MusicMCP.AI api Server - HTTP call MusicMCP.AI API for MCP"""
    mcp.run()


if __name__ == "__main__":
    main()
