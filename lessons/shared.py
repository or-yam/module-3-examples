"""Shared helpers for every lesson.

Kept in one place so each lesson file is about the concept, not setup.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()

__all__ = ["get_llm"]

DEFAULT_MODEL = os.getenv("BALANCED_MODEL", "open-weight-smart")


def get_llm(model: str | None = None) -> ChatOpenAI:
    """Return a chat model pointed at Tikal's hosted LiteLLM proxy.

    ChatOpenAI, not langchain-litellm: we call the proxy's HTTP API and it
    speaks the OpenAI wire format. So bare model names only —
    "openai:gpt-4" 403s.
    """
    api_key = os.getenv("LITELLM_API_KEY")
    if not api_key:
        raise RuntimeError(
            "LITELLM_API_KEY not set. Run `cp .env.example .env`, then fill it in."
        )

    return ChatOpenAI(
        model=model or DEFAULT_MODEL,
        api_key=SecretStr(api_key),
        base_url=os.getenv("LITELLM_PROXY_URL", "https://litellm.tikalk.dev"),
    )
