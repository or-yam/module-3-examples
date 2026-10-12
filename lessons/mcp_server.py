"""A tiny local MCP server for lesson 5."""

from fastmcp import FastMCP

mcp = FastMCP("Calculator")


@mcp.tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


if __name__ == "__main__":
    mcp.run(transport="stdio")
