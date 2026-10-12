"""Lesson 5 — Discover tools from an MCP server."""

from contextlib import asynccontextmanager
from pathlib import Path

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter

from lessons.shared import get_llm


@asynccontextmanager
async def graph():
    """Connect to the server and keep it open while the agent runs."""
    server = Path(__file__).with_name("mcp_server.py")
    async with MCPAdapter(server) as adapter:
        tools = await adapter.list_tools()
        yield create_agent(
            model=get_llm(),
            tools=tools,
            system_prompt="Use the addition tool for arithmetic.",
        )
