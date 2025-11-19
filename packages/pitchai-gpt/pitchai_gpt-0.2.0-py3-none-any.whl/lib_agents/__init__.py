"""Shared GPT helpers and the Fast Streaming Agent runtime."""

from .gpt.gpt import GPT  # noqa: F401
from .gpt.prompt_loader import PromptLoader, Prompts  # noqa: F401

GPTClient = GPT  # Backwards compatibility alias

__all__ = ["GPT", "GPTClient", "PromptLoader", "Prompts"]
