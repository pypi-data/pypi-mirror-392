"""Utilities for preloading FastStreamingAgent dataframes at container startup."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from .config_resolver import resolve_agent_config_path_sync
from .main import FastStreamingAgent
from .preloaded_state import cache_preloaded_state, has_preloaded_state

LOGGER = logging.getLogger(__name__)


def _normalise_path(path: str | Path) -> str:
    return str(Path(path).resolve())


def preload_agent_state(
    *,
    chatconfig_id: Optional[str] = None,
    config_path: Optional[str] = None,
    force: bool = False,
) -> str:
    """Instantiate an agent and cache its base/semantic dataframes for reuse."""

    resolved_path = config_path
    if resolved_path is None:
        lookup_id = chatconfig_id or "gzb"
        resolved_path = resolve_agent_config_path_sync(lookup_id)
    normalised_path = _normalise_path(resolved_path)

    if not force and has_preloaded_state(normalised_path):
        LOGGER.info("Dataframes already preloaded for %s; skipping.", normalised_path)
        return normalised_path

    import os

    LOGGER.info(
        "Preloading FastStreamingAgent dataframes for %s (chatconfig: %s) [pid=%s]",
        normalised_path,
        chatconfig_id or "<unknown>",
        os.getpid(),
    )

    agent = FastStreamingAgent(
        agent_config=normalised_path,
        enable_suggestions=False,
        testing=True,
    )
    if chatconfig_id:
        agent.chatconfig_id = chatconfig_id

    base_sources = getattr(agent, "_base_dataframe_sources", {})
    semantic_registry = getattr(agent, "semantic_layer_registry", {})
    dataframe_format = agent.config.get_dataframe_load_settings().format

    cache_preloaded_state(
        config_path=normalised_path,
        dataframe_format=dataframe_format,
        base_frames=base_sources,
        semantic_registry=semantic_registry,
    )

    LOGGER.info(
        "Cached %d base dataframes and %d semantic layers for %s",
        len(base_sources),
        len(semantic_registry),
        normalised_path,
    )

    # Explicitly drop the agent to release the temporarily loaded frames.
    del agent

    return normalised_path


__all__ = ["preload_agent_state"]
