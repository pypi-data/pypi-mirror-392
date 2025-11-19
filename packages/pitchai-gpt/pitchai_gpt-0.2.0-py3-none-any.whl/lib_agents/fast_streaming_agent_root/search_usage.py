"""Helpers for tracking fuzzy_search usage and emitting UI chips."""

from __future__ import annotations

import asyncio
import inspect
from functools import wraps
from typing import Any, Callable

SEARCH_ICON = "fa-solid fa-magnifying-glass"


def install_search_wrappers(agent: Any) -> None:
    """Wrap fuzzy_search so we can emit UI events with the actual query."""

    execution_functions = getattr(agent, "execution_functions", {})
    func = execution_functions.get("fuzzy_search")
    if not callable(func):
        return
    if getattr(func, "_search_usage_wrapped", False):
        return

    try:
        signature = inspect.signature(func)
    except (ValueError, TypeError):
        signature = None

    def _extract_query(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        query_value = None
        if signature is not None:
            try:
                bound = signature.bind_partial(*args, **kwargs)
                query_value = bound.arguments.get("query")
            except Exception:  # pragma: no cover - defensive
                query_value = None
        else:
            if len(args) >= 3:
                query_value = args[2]
            elif "query" in kwargs:
                query_value = kwargs.get("query")
        return query_value

    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            query_value = _extract_query(args, kwargs)
            result = await func(*args, **kwargs)
            if query_value:
                _schedule_search_emit(agent, query_value)
            return result

        async_wrapper._search_usage_wrapped = True  # type: ignore[attr-defined]
        execution_functions["fuzzy_search"] = async_wrapper
        return

    @wraps(func)
    def wrapper(*args, **kwargs):
        query_value = _extract_query(args, kwargs)
        result = func(*args, **kwargs)
        if query_value:
            _schedule_search_emit(agent, query_value)
        return result

    wrapper._search_usage_wrapped = True  # type: ignore[attr-defined]
    execution_functions["fuzzy_search"] = wrapper


async def _emit_search_usage(agent: Any, query: str) -> None:
    """Render a topline chip highlighting the fuzzy search query."""

    shared_ui_msg = getattr(agent, "shared_ui_msg", None)
    templates = getattr(agent, "templates", None)
    pseudo_request = getattr(agent, "standard_pseudo_request", None)

    if not (shared_ui_msg and templates and pseudo_request):
        return

    safe_query = (query or "").strip()
    if len(safe_query) > 80:
        safe_query = safe_query[:77] + "..."
    if not safe_query:
        return

    label = f'Fuzzy search · "{safe_query}"'

    try:
        rendered = templates.TemplateResponse(
            pseudo_request,
            "components/search_done.html",
            {
                "search_term": label,
                "clickable_url": None,
                "is_clickable": False,
                "icon_url": None,
                "fa_icon": SEARCH_ICON,
                "source_index": "fuzzy_search",
            },
        ).body.decode("utf-8")
    except Exception as exc:  # pragma: no cover - defensive rendering
        logger = getattr(agent, "logger", None)
        if logger:
            logger.debug("Failed to render fuzzy search chip for %s: %s", safe_query, exc)
        return

    try:
        await shared_ui_msg.set_content_instantly(
            rendered,
            "topline",
            overwrite=False,
            skip_grpc=True,
        )
    except Exception as exc:  # pragma: no cover - UI failures
        logger = getattr(agent, "logger", None)
        if logger:
            logger.debug("Failed to stream fuzzy search chip for %s: %s", safe_query, exc)
def _schedule_search_emit(agent: Any, query_value: Any) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop:
        loop.create_task(_emit_search_usage(agent, str(query_value)))
