"""Helpers for streaming dataset usage chips from FastStreamingAgent."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any
import re

from .stream_inspector import DatasetUsageObserver, DatasetInfo, generate_aliases

if TYPE_CHECKING:  # pragma: no cover
    from .main import FastStreamingAgent


def _friendly_label(source: str, *, prefer_schema: bool = False) -> str:
    """Return a short, human-friendly label derived from a datasource string."""

    candidate = source or ""
    if "#" in candidate:
        candidate = candidate.split("#", 1)[1]
    candidate = candidate.split("/")[-1]
    if "." in candidate:
        parts = candidate.split(".", 1)
        candidate = parts[0] if prefer_schema else parts[-1]
    candidate = candidate.replace("_", " ").strip()
    return candidate.title() if candidate else source


def normalize_dataset_key(dataset_id: str) -> str:
    """Return a slug-safe key for matching dataset usage events to UI elements."""

    if not dataset_id:
        return ""
    core = dataset_id.split("::", 1)[-1]
    return re.sub(r"[^a-z0-9]+", "-", core.lower()).strip("-")


def build_dataset_alias_map(agent: "FastStreamingAgent") -> Dict[str, DatasetInfo]:
    """Collect all aliases that should trigger dataset usage events."""

    insights = getattr(agent.config, "stream_insights", None)
    if not insights or not insights.enabled:
        return {}

    alias_map: Dict[str, DatasetInfo] = {}
    df_id_to_info: Dict[int, DatasetInfo] = {}
    semantic_df_map: Dict[int, DatasetInfo] = {}

    if insights.emit_base_dataframes:
        # Include configured dataframe names even before they are loaded so
        # references in streamed code still emit UI chips.
        try:
            df_settings = agent.config.get_dataframe_load_settings()
            configured_names = (
                df_settings.normalized_paths()
                if hasattr(df_settings, "normalized_paths")
                else list(df_settings)
            )
        except Exception:
            configured_names = []

        base_sources = getattr(agent, "_base_dataframe_sources", {}) or {}
        for logical_name, dataframe in base_sources.items():
            stem = _friendly_label(str(logical_name))
            info = DatasetInfo(
                dataset_id=f"base::{logical_name}",
                display_name=stem,
                source_type="base",
                description=str(logical_name),
            )
            df_id_to_info[id(dataframe)] = info
            for alias in generate_aliases(logical_name):
                if alias:
                    alias_map.setdefault(alias.lower(), info)

        for logical_name in configured_names:
            if not logical_name:
                continue
            logical_name_str = str(logical_name)
            stem = _friendly_label(logical_name_str, prefer_schema=False)
            info = DatasetInfo(
                dataset_id=f"config::{logical_name_str}",
                display_name=stem,
                source_type="config",
                description=logical_name_str,
            )
            candidate_aliases = set(generate_aliases(logical_name_str))
            if "#" in logical_name_str:
                table_spec = logical_name_str.split("#", 1)[1]
                candidate_aliases.update(generate_aliases(table_spec))
            for alias in candidate_aliases:
                if alias:
                    alias_map[alias.lower()] = info

        if insights.emit_semantic_layers:
            registry = getattr(agent, "semantic_layer_registry", {}) or {}
            for name, entry in registry.items():
                info = DatasetInfo(
                    dataset_id=f"semantic::{name}",
                    display_name=name,
                    source_type="semantic",
                    description=getattr(entry, "description", None),
                )
                semantic_df_map[id(entry.dataframe)] = info
                for alias in generate_aliases(name):
                    if alias:
                        alias_map[alias.lower()] = info

    for alias, dataframe in (agent.loaded_dataframes or {}).items():
        info = df_id_to_info.get(id(dataframe))
        if info and alias:
            alias_map.setdefault(alias.lower(), info)

    exec_globals = getattr(agent, "execution_globals", {}) or {}
    for alias, value in exec_globals.items():
        if not alias:
            continue
        info = df_id_to_info.get(id(value)) or semantic_df_map.get(id(value))
        if info:
            alias_map.setdefault(alias.lower(), info)

    return alias_map


def create_dataset_usage_observer(agent: "FastStreamingAgent"):
    """Create a DatasetUsageObserver instance tied to the agent."""

    insights = getattr(agent.config, "stream_insights", None)
    if not insights or not insights.enabled:
        return None

    if not getattr(agent, "_dataset_alias_map", None):
        agent._dataset_alias_map = build_dataset_alias_map(agent)
    if not agent._dataset_alias_map:
        return None

    if not hasattr(agent, "_dataset_alias_logged"):
        sample_keys = ", ".join(sorted(agent._dataset_alias_map.keys())[:10])
        agent.logger.info("Dataset alias sample: %s", sample_keys)
        agent._dataset_alias_logged = True

    if not (
        getattr(agent, "shared_ui_msg", None)
        and getattr(agent, "templates", None)
        and getattr(agent, "standard_pseudo_request", None)
    ):
        return None

    async def notify(info: DatasetInfo) -> None:
        await emit_dataset_usage(agent, info)

    return DatasetUsageObserver(
        {alias: info for alias, info in agent._dataset_alias_map.items()},
        notify,
        max_events=max(1, insights.max_events or 1),
    )


async def emit_dataset_usage(agent: "FastStreamingAgent", info: DatasetInfo) -> None:
    """Render and stream a dataset usage chip via the shared UI message."""

    if info.dataset_id in agent._dataset_events_emitted:
        return

    agent._dataset_events_emitted.add(info.dataset_id)

    shared_ui_msg = getattr(agent, "shared_ui_msg", None)
    templates = getattr(agent, "templates", None)
    pseudo_request = getattr(agent, "standard_pseudo_request", None)

    if not (shared_ui_msg and templates and pseudo_request):
        agent.logger.info("Dataset usage skipped - missing UI context")
        return

    agent.logger.info("Dataset usage detected: %s", info.display_name)

    icon_class = getattr(getattr(agent.config, "stream_insights", None), "icon_class", "fa-solid fa-table")

    try:
        rendered = templates.TemplateResponse(
            pseudo_request,
            "components/search_done.html",
            {
                "search_term": info.display_name,
                "clickable_url": None,
                "is_clickable": False,
                "icon_url": None,
                "fa_icon": icon_class,
                "source_index": info.source_type,
            },
        ).body.decode("utf-8")
    except Exception as exc:  # pragma: no cover - defensive rendering
        agent.logger.debug("Failed to render dataset usage chip for %s: %s", info.dataset_id, exc)
        return

    try:
        await shared_ui_msg.set_content_instantly(
            rendered,
            "topline",
            overwrite=False,
            skip_grpc=True,
        )
    except Exception as exc:  # pragma: no cover - UI failures
        agent.logger.debug("Failed to stream dataset usage for %s: %s", info.dataset_id, exc)

    conversation_id = getattr(shared_ui_msg, "conversation_id", None)
    dataset_key = normalize_dataset_key(info.dataset_id)
    if conversation_id and dataset_key:
        payload: dict[str, Any] = {
            "event": "data-source-activate",
            "data": {
                "dataset_id": info.dataset_id,
                "dataset_key": dataset_key,
                "display_name": info.display_name,
            },
        }
        try:
            await shared_ui_msg.msg_mngr.broadcast_event(conversation_id, payload)
        except Exception as exc:  # pragma: no cover - defensive logging
            agent.logger.debug("Failed to broadcast dataset activation for %s: %s", info.dataset_id, exc)
