from langchain.agents import create_agent
from langchain_tavily import TavilySearch

from lessons.shared import get_llm

graph = create_agent(
    model=get_llm(),
    tools=[TavilySearch(max_results=3)],
    system_prompt="Search the web before answering. Cite the source URLs.",
)
