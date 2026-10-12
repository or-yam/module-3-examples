from time import sleep

from langchain.agents import create_agent  # noqa: D100
from langchain.tools import tool

from lessons.shared import get_llm


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The city name, e.g. "Lisbon".
    """
    sleep(3)
    return f"It's always sunny and 22C in {city}."


agent = create_agent(
    model=get_llm(),
    system_prompt="You are a helpful assistant.",
    tools=[get_weather],
)

graph = agent
