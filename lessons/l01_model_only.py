from lessons.shared import get_llm


def main() -> None:
    """Send one request and print the assistant response."""
    model = get_llm()
    messages = [
        {"role": "system", "content": "You are a terse assistant. One sentence max."},
        {"role": "user", "content": "How to make chocolate cake?"},
    ]
    response = model.invoke(messages)
    print(response.content)


if __name__ == "__main__":
    main()
