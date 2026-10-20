from lessons.shared import get_llm


def main() -> None:
    """Chat until the user exits or closes standard input."""
    model = get_llm()
    chat_messages = [
        {"role": "system", "content": "You are a terse assistant. One sentence max."}
    ]
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue
        chat_messages.append({"role": "user", "content": user_input})
        response = model.invoke(chat_messages)
        print(f"Assistant: {response.content}")
        chat_messages.append(response)


if __name__ == "__main__":
    main()
