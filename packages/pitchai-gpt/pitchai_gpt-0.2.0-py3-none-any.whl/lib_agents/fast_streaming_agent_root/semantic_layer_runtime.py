"""Runtime helpers for semantic-layer dataframe materialisation and discovery."""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import polars as pl

from lib_search.index import add_documents, ensure_index
from lib_search.search import search as semantic_search
from libs.lib_utils.src.lib_utils.code_ops.aexec import sync_execute_catch_logs_errors

from .agent_config import SemanticLayerDefinition

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class SemanticLayerEntry:
    """Materialised semantic-layer dataframe and related metadata."""

    name: str
    description: str
    dataframe: pd.DataFrame
    dependencies: list[str]
    code: str
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    logs: str | None = None
    columns: list[str] = field(default_factory=list)
    row_count: int = 0
    preview_markdown: str = ""


def _get_logger(agent: Any) -> logging.Logger:
    return getattr(agent, "logger", LOGGER)


def _resolve_repo_path(project_root: Path | None, agent: Any) -> str:
    if project_root is not None:
        return str(project_root)
    repo_path = getattr(agent, "project_root", None)
    if isinstance(repo_path, Path):
        return str(repo_path)
    return "."


def _normalise_dataframe(result: Any) -> pd.DataFrame | None:
    if result is None:
        return None
    if isinstance(result, pd.DataFrame):
        return result
    if isinstance(result, pl.DataFrame):
        return result.to_pandas()
    if hasattr(result, "to_pandas"):
        try:
            converted = result.to_pandas()
            if isinstance(converted, pd.DataFrame):
                return converted
        except Exception:  # pragma: no cover - third-party conversions
            return None
    return None


def _generate_preview(df: pd.DataFrame, *, max_rows: int = 5) -> str:
    truncated = df.head(max_rows)
    try:
        return truncated.to_markdown(index=False)
    except Exception:  # pragma: no cover - markdown dependency issues
        return truncated.to_string(index=False)


def load_semantic_layer_dataframes(agent: Any, project_root: Path | None = None) -> dict[str, SemanticLayerEntry]:
    """Evaluate semantic-layer definitions and register resulting dataframes.

    Returns:
        Mapping of semantic layer name to metadata entries.
    """
    from .dataframe_loader import _register_dataframe  # Local import to avoid circular dependency
    from .preloaded_state import get_preloaded_semantic_layers
    config = getattr(agent, "config", None)
    if config is None:
        return {}

    definitions = config.get_semantic_layer_definitions()
    logger = _get_logger(agent)

    registry: dict[str, SemanticLayerEntry] = {}
    failures: list[dict[str, Any]] = []
    setattr(agent, "semantic_layer_registry", registry)
    setattr(agent, "semantic_layer_failures", failures)

    if not definitions:
        return registry

    execution_globals = getattr(agent, "execution_globals", {})
    if not isinstance(execution_globals, dict):
        logger.warning("Semantic layer runtime expects execution_globals to be a dict; skipping definitions.")
        return registry

    execution_globals.setdefault("pd", pd)
    execution_globals.setdefault("pl", pl)

    repo_path = _resolve_repo_path(project_root, agent)

    # Track aliases registered in this pass to avoid duplicates per definition.
    registered_aliases: dict[str, Any] = {}

    agent_config_path = getattr(agent, "agent_config_path", None)
    preloaded_registry = get_preloaded_semantic_layers(agent_config_path)
    logger.info(
        "Semantic preload lookup for %s: %s",
        agent_config_path or "<unknown>",
        "hit" if preloaded_registry else "miss",
    )
    cold_load_allowed = bool(getattr(agent, "testing", False))
    if preloaded_registry is not None:
        for name, entry in preloaded_registry.items():
            registry[name] = entry
            _register_dataframe(agent, name, entry.dataframe, registered_aliases)

        if registered_aliases:
            agent.execution_runtime.refresh_protected_names()
            logger.info(
                "Reused preloaded semantic-layer dataframes: %s",
                ", ".join(sorted(registry.keys())),
            )

        return registry
    elif not cold_load_allowed:
        raise RuntimeError(
            f"No preloaded semantic layers found for config {agent_config_path!r}. "
            "Warm-up must complete successfully before creating agents."
        )
    else:
        logger.info(
            "Cold-computing semantic layers for %s (testing=%s)",
            agent_config_path or "<unknown>",
            cold_load_allowed,
        )

    for definition in definitions:
        logger.info("Evaluating semantic layer '%s'", definition.name)
        missing_dependencies = [
            dependency
            for dependency in definition.dependencies
            if dependency not in execution_globals
        ]

        if missing_dependencies:
            message = f"Skipping semantic layer '{definition.name}' because dependencies were missing: {', '.join(sorted(missing_dependencies))}"
            logger.warning(message)
            failures.append({"name": definition.name, "reason": message})
            continue

        # Clear previous `result` bindings to avoid cross-contamination.
        execution_globals.pop("result", None)

        try:
            success, _, logs = sync_execute_catch_logs_errors(
                definition.code,
                execution_globals,
                repo_path=repo_path,
            )
        except Exception as exc:  # pragma: no cover - execution runtime failure
            message = f"Failed to execute semantic layer '{definition.name}': {exc}"
            logger.exception(message)
            failures.append({"name": definition.name, "reason": message})
            continue

        if not success:
            message = f"Semantic layer '{definition.name}' raised an error during execution."
            logger.error("%s Logs:\n%s", message, logs)
            failures.append({"name": definition.name, "reason": message, "logs": logs})
            continue

        result = execution_globals.get("result")
        dataframe = _normalise_dataframe(result)
        if dataframe is None:
            message = (
                f"Semantic layer '{definition.name}' did not return a pandas DataFrame. "
                "Ensure the code assigns a pandas DataFrame to the variable `result`."
            )
            logger.error(message)
            failures.append({"name": definition.name, "reason": message})
            continue

        dataframe = dataframe.copy()
        entry = SemanticLayerEntry(
            name=definition.name,
            description=definition.description,
            dataframe=dataframe,
            dependencies=list(definition.dependencies),
            code=definition.code,
            logs=logs,
            columns=[str(column) for column in dataframe.columns],
            row_count=int(dataframe.shape[0]),
            preview_markdown=_generate_preview(dataframe),
        )

        # Prevent overwriting an existing binding silently.
        if definition.name in execution_globals and definition.name not in registry:
            logger.warning(
                "Semantic layer '%s' would overwrite an existing global with the same name; skipping registration.",
                definition.name,
            )
            failures.append({
                "name": definition.name,
                "reason": f"Global '{definition.name}' already exists; choose a different semantic layer name.",
            })
            continue

        _register_dataframe(agent, definition.name, entry.dataframe, registered_aliases)
        registry[definition.name] = entry

    if registered_aliases:
        agent.execution_runtime.refresh_protected_names()
        logger.info(
            "Semantic layer dataframes registered: %s",
            ", ".join(sorted(registry.keys())),
        )

    return registry


def _resolve_chatconfig_id(agent: Any) -> str:
    explicit = getattr(agent, "chatconfig_id", None)
    if explicit:
        return str(explicit)
    chat_config = getattr(agent, "chat_config", None)
    if chat_config is not None:
        chat_config_id = getattr(chat_config, "id", None)
        if chat_config_id:
            return str(chat_config_id)
    config_path = getattr(agent, "agent_config_path", None)
    if config_path:
        return Path(config_path).stem
    return "default"


def _build_index_name(agent: Any) -> str:
    prefix = os.getenv("SEMANTIC_LAYER_INDEX_PREFIX", "afasask-semantic-index")
    chatconfig_id = _resolve_chatconfig_id(agent)
    safe_scope = re.sub(r"[^a-zA-Z0-9_-]", "_", chatconfig_id.lower())
    return f"{prefix}-{safe_scope}"


def _build_document_id(agent: Any, entry: SemanticLayerEntry) -> str:
    chatconfig_id = _resolve_chatconfig_id(agent)
    return f"{chatconfig_id}:{entry.name}"


def _build_document_payload(agent: Any, entry: SemanticLayerEntry) -> dict[str, Any]:
    return {
        "id": _build_document_id(agent, entry),
        "content": "\n".join([
            f"Semantic Layer: {entry.name}",
            f"Description: {entry.description}",
            f"Columns: {', '.join(entry.columns)}",
            f"Row count: {entry.row_count}",
            "",
            "Preview:",
            entry.preview_markdown,
        ]),
        "name": entry.name,
        "description": entry.description,
        "columns": entry.columns,
        "row_count": entry.row_count,
        "dependencies": entry.dependencies,
        "chatconfig_id": _resolve_chatconfig_id(agent),
        "preview": entry.preview_markdown,
        "created_at": entry.created_at.isoformat(),
    }


async def ensure_semantic_layer_index(agent: Any, *, force: bool = False) -> None:
    """Ensure semantic-layer metadata is indexed in Voyage/Qdrant."""
    registry: dict[str, SemanticLayerEntry] = getattr(agent, "semantic_layer_registry", {})
    if not registry:
        setattr(agent, "_semantic_layer_indexed", True)
        return

    if getattr(agent, "_semantic_layer_indexed", False) and not force:
        return

    index_name = _build_index_name(agent)
    logger = _get_logger(agent)
    documents = [_build_document_payload(agent, entry) for entry in registry.values()]

    if not documents:
        setattr(agent, "_semantic_layer_indexed", True)
        return

    try:
        await ensure_index(index_name)
        await add_documents(index_name, documents, ensure_collection=False)
        setattr(agent, "_semantic_layer_indexed", True)
        logger.info("Semantic layer index '%s' updated with %d documents.", index_name, len(documents))
    except Exception as exc:  # pragma: no cover - network/path errors
        logger.warning("Failed to update semantic layer index '%s': %s", index_name, exc)
        setattr(agent, "_semantic_layer_indexed", False)


def _build_search_result(entry: SemanticLayerEntry, *, score: float | None = None) -> dict[str, Any]:
    return {
        "name": entry.name,
        "description": entry.description,
        "score": score,
        "columns": entry.columns,
        "row_count": entry.row_count,
        "preview": entry.preview_markdown,
    }


async def search_semantic_layers(
    agent: Any,
    query: str | None = None,
    *,
    top_k: int = 5,
    score_threshold: float | None = None,
    filter_name: str | None = None,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Run semantic search over indexed semantic-layer definitions."""
    registry: dict[str, SemanticLayerEntry] = getattr(agent, "semantic_layer_registry", {})
    if not registry:
        return []
    if kwargs:
        _get_logger(agent).warning(
            "Ignoring unsupported keyword arguments for search_semantic_layers: %s",
            ", ".join(sorted(str(key) for key in kwargs)),
        )

    try:
        top_k_int = int(top_k)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"top_k must be an integer; received {top_k!r}") from exc

    if top_k_int <= 0:
        return []

    filter_name = filter_name or None
    if filter_name is not None:
        filter_name = str(filter_name)

    query_str = (query or "").strip()
    if not query_str:
        entries = list(registry.values())
        if filter_name:
            entries = [entry for entry in entries if entry.name == filter_name]
            if not entries:
                fallback = registry.get(filter_name)
                if fallback is not None:
                    entries = [fallback]
        entries.sort(key=lambda entry: (-entry.row_count, entry.name.lower()))
        return [_build_search_result(entry, score=None) for entry in entries[:top_k_int]]

    await ensure_semantic_layer_index(agent)
    index_name = _build_index_name(agent)

    try:
        results = await semantic_search(index_name, query_str, limit=top_k_int, score_threshold=score_threshold)
    except Exception as exc:  # pragma: no cover - index missing / network
        _get_logger(agent).warning("Semantic layer search failed: %s", exc)
        return []

    output: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    for result in results:
        metadata = result.metadata or {}
        name = metadata.get("name")
        entry = registry.get(name)
        if entry is None and not name:
            continue
        record = {
            "name": name or (entry.name if entry else None),
            "description": metadata.get("description") or (entry.description if entry else ""),
            "score": result.score,
            "columns": metadata.get("columns") or (entry.columns if entry else []),
            "row_count": metadata.get("row_count") or (entry.row_count if entry else 0),
            "preview": metadata.get("preview") or (entry.preview_markdown if entry else ""),
        }
        if record["name"] is None:
            continue
        if filter_name and record["name"] != filter_name:
            continue
        if record["name"] in seen_names:
            continue
        seen_names.add(record["name"])
        output.append(record)

    if filter_name and not output:
        entry = registry.get(filter_name)
        if entry is not None:
            output.append(_build_search_result(entry, score=None))

    if not output and not filter_name:
        entries = sorted(registry.values(), key=lambda entry: (-entry.row_count, entry.name.lower()))
        output = [_build_search_result(entry, score=None) for entry in entries[:top_k_int]]

    return output


def list_semantic_layers(agent: Any) -> list[dict[str, Any]]:
    """Return metadata for all materialised semantic-layer dataframes."""
    registry: dict[str, SemanticLayerEntry] = getattr(agent, "semantic_layer_registry", {})
    if not registry:
        return []

    return [
        {
            "name": entry.name,
            "description": entry.description,
            "columns": entry.columns,
            "row_count": entry.row_count,
            "preview": entry.preview_markdown,
            "dependencies": entry.dependencies,
            "created_at": entry.created_at.isoformat(),
        }
        for entry in sorted(registry.values(), key=lambda item: item.name.lower())
    ]
