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

graph = agent


if __name__ == "__main__":
    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Lisbon is sunny and 22°C. Outdoor work is comfortable. Return a weather report.",
                }
            ]
        }
    )
    report = result["structured_response"]
    print(report.model_dump_json(indent=2))
    print(f"Temperature: {report.temperature_c}°C")
