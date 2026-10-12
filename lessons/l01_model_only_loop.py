from lessons.shared import get_llm

model = get_llm()
chat_messages = messages = [
    {
        "role": "system",
        "content": "You are a terse assistant. One sentence max.",
    }
]

# simple chat via cli, getting user input and responding

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    chat_messages.append({"role": "user", "content": user_input})
    response = model.invoke(chat_messages)
    print(f"Assistant: {response.content}")
    chat_messages.append({"role": "assistant", "content": response.text})
