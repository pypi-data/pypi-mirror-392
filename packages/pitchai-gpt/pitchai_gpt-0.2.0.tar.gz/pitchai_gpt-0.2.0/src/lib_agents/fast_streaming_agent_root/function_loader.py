"""Helpers for loading configured callables into the agent runtime."""

from __future__ import annotations

import importlib
import inspect
from functools import wraps
from typing import Any, Callable, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .agent_config import AgentConfig


def load_configured_functions(
    config: "AgentConfig",
    execution_globals: Dict[str, Any],
    agent: Any | None = None,
) -> None:
    """Populate *execution_globals* with functions declared in the agent config."""
    for func_config in config.functions.available_functions:
        # Only load functions that have a module path. Remaining internal functions
        # (stop, task, todo_write, etc.) are registered elsewhere during runtime.
        if func_config.module_path and func_config.function_name:
            module = importlib.import_module(func_config.module_path)
            func = getattr(module, func_config.function_name)
            execution_globals[func_config.name] = _wrap_with_agent_context(func, agent)
            continue

        if func_config.name == "test":
            from fast_streaming_agent.default_functions import test

            execution_globals["test"] = test


def _wrap_with_agent_context(func: Callable[..., Any], agent: Any | None) -> Callable[..., Any]:
    """Inject agent context into *func* if it declares supported parameters."""
    if agent is None:
        return func

    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        return func

    context_providers = _build_context_providers(agent)
    required_keys = {
        name: provider
        for name, provider in context_providers.items()
        if name in signature.parameters
    }

    if not required_keys:
        return func

    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            for key, provider in required_keys.items():
                kwargs.setdefault(key, provider())
            return await func(*args, **kwargs)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        for key, provider in required_keys.items():
            kwargs.setdefault(key, provider())
        return func(*args, **kwargs)

    return sync_wrapper


def _build_context_providers(agent: Any) -> Dict[str, Callable[[], Any]]:
    """Create provider callables that capture agent state lazily."""

    def conversation_id() -> Any:
        return getattr(agent, "conversation_id", None)

    def chatconfig_id() -> Any:
        explicit = getattr(agent, "chatconfig_id", None)
        if explicit:
            return explicit
        chat_config = getattr(agent, "chat_config", None)
        return getattr(chat_config, "id", None) if chat_config is not None else None

    def chat_config() -> Any:
        return getattr(agent, "chat_config", None)

    def shared_ui_msg() -> Any:
        return getattr(agent, "shared_ui_msg", None)

    def templates() -> Any:
        return getattr(agent, "templates", None)

    def standard_pseudo_request() -> Any:
        return getattr(agent, "standard_pseudo_request", None)

    return {
        "agent": lambda: agent,
        "conversation_id": conversation_id,
        "chatconfig_id": chatconfig_id,
        "chat_config": chat_config,
        "shared_ui_msg": shared_ui_msg,
        "ui_msg": shared_ui_msg,
        "templates": templates,
        "standard_pseudo_request": standard_pseudo_request,
    }
