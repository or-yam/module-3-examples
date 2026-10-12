"""Lesson 4 — A Pydantic schema as the model's output contract."""

from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from pydantic import BaseModel, Field

from lessons.shared import get_llm


class WeatherReport(BaseModel):
    """A structured weather summary."""

    city: str = Field(description="The city the report is about.")
    temperature_c: int = Field(description="Temperature in Celsius.")
    is_workable_outdoors: bool = Field(
        description="True if the weather suits outdoor work."
    )


agent = create_agent(
    model=get_llm(),
    response_format=ProviderStrategy(WeatherReport),
)

res = agent.invoke(
    {"messages": [{"role": "user", "content": "תמציא לי מזג אוויר בתל אביב"}]}
)


print(res)

graph = agent
