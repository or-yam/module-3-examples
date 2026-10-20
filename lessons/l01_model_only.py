from langchain_core.messages import HumanMessage
from langchain_core.messages.system import SystemMessage

from lessons.shared import get_llm

model = get_llm()


system_prompt = {
    "role": "system",
    "content": "You are a terse assistant. One sentence max.",
}
messages = [
    SystemMessage("You are a terse assistant. One sentence max."),
    HumanMessage("How to make chocolate cake?"),
    {
        "role": "user",
        "content": "How to make chocolate cake?",
    },
]

# response = model.invoke(messages)
#
# print(response.content)
