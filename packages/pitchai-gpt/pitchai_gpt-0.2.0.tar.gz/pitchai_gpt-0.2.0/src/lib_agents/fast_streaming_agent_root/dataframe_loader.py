"""Helpers for loading configured dataframes into the agent runtime."""

from __future__ import annotations

import logging
import os
import re
import uuid
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import polars as pl
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from libs.lib_utils.src.lib_utils.code_ops.aexec import sync_execute_catch_logs_errors

from .preloaded_state import get_preloaded_base_dataframes
from configs import server_config


def load_configured_dataframes(agent: Any, project_root: Path) -> dict[str, Any]:
    """Load dataframes declared in the agent configuration into execution globals.

    Args:
        agent: Instance of :class:`FastStreamingAgent`.
        project_root: Root directory of the repository for resolving relative paths.

    Returns:
        Mapping from config source string to the loaded :class:`polars.DataFrame`.
    """

    config = getattr(agent, "config", None)
    if config is None or not getattr(config, "load_state_dataframes", True):
        setattr(agent, "_base_dataframe_sources", {})
        return {}

    settings = config.get_dataframe_load_settings()
    sources = settings.normalized_sources() if hasattr(settings, "normalized_sources") else settings.normalized_paths()
    if not sources:
        setattr(agent, "_base_dataframe_sources", {})
        return {}

    logger = getattr(agent, "logger", logging.getLogger(__name__))

    def _extract_logical_name(entry: Any) -> str:
        if isinstance(entry, dict):
            return str(entry.get("logical_name", "")).strip()
        return str(entry or "").strip()

    has_database_sources = any(
        _is_database_source(_extract_logical_name(entry)) for entry in sources if _extract_logical_name(entry)
    )

    base_dir: Path | None = None
    try:
        from configs.db_config import DB_FILES_DENORMALIZED_PATH
    except ImportError as exc:  # pragma: no cover - configuration issue
        logger.warning("Unable to import DB configuration: %s", exc)
    else:
        base_dir = Path(DB_FILES_DENORMALIZED_PATH)
        if not base_dir.is_absolute():
            base_dir = (project_root / base_dir).resolve()

    registered_aliases: dict[str, Any] = {}

    config_key = getattr(agent, "agent_config_path", None)
    preloaded_payload = get_preloaded_base_dataframes(config_key)
    logger.info(
        "Preload lookup for %s: %s",
        config_key or "<unknown>",
        "hit" if preloaded_payload else "miss",
    )
    cold_load_allowed = bool(getattr(agent, "testing", False) or has_database_sources)

    if preloaded_payload is None and not cold_load_allowed:
        raise RuntimeError(
            f"No preloaded dataframes found for config {config_key!r}. "
            "Warm-up must complete successfully before creating agents."
        )

    preloaded_frames: dict[str, Any] | None = None
    dataframe_format = settings.format

    if preloaded_payload is not None:
        preload_format, stored_frames = preloaded_payload
        dataframe_format = preload_format or dataframe_format
        preloaded_frames = stored_frames

    if dataframe_format == "pandas":
        agent.execution_functions.setdefault("pd", pd)
        agent.execution_runtime.system_bindings.setdefault("pd", pd)
        agent.execution_globals.setdefault("pd", pd)
    else:
        agent.execution_functions.setdefault("pl", pl)
        agent.execution_runtime.system_bindings.setdefault("pl", pl)
        agent.execution_globals.setdefault("pl", pl)

    loaded_sources: dict[str, Any] = {}

    if preloaded_frames is not None:
        logger.info(
            "Reusing preloaded base dataframes for %s", config_key or "<unknown>"
        )
        for logical_name, dataframe in preloaded_frames.items():
            if not logical_name:
                continue
            loaded_sources[logical_name] = dataframe
            _register_dataframe(agent, logical_name, dataframe, registered_aliases)

        if registered_aliases:
            agent.execution_runtime.refresh_protected_names()
            logger.info(
                "Reused preloaded dataframes for config %s: %s",
                config_key or "<unknown>",
                ", ".join(sorted(registered_aliases.keys())),
            )

        _publish_dataframe_registry(agent, registered_aliases)
        setattr(agent, "_base_dataframe_sources", loaded_sources)
        return registered_aliases

    # No preloaded dataframes available; only permitted during warm-up/testing.
    logger.info(
        "Cold-loading dataframes for %s (testing=%s)",
        config_key or "<unknown>",
        cold_load_allowed,
    )

    for source in sources:
        if isinstance(source, dict):
            logical_name = str(source.get("logical_name", "")).strip()
            extra_candidates = source.get("candidates", [])
        else:
            logical_name = str(source or "").strip()
            extra_candidates = None
        if not logical_name:
            continue

        dataframe = _load_single_dataframe(
            logical_name,
            base_dir,
            project_root,
            logger,
            dataframe_format,
            extra_candidates=extra_candidates,
        )
        if dataframe is None:
            continue

        dataframe = _apply_preprocessing(
            agent=agent,
            logical_name=logical_name,
            dataframe=dataframe,
            dataframe_format=dataframe_format,
            project_root=project_root,
            logger=logger,
        )

        loaded_sources[logical_name] = dataframe
        _register_dataframe(agent, logical_name, dataframe, registered_aliases)

    if registered_aliases:
        agent.execution_runtime.refresh_protected_names()
        logger.info(
            "Loaded dataframes into execution globals: %s",
            ", ".join(sorted(registered_aliases.keys())),
        )

    _publish_dataframe_registry(agent, registered_aliases)
    setattr(agent, "_base_dataframe_sources", loaded_sources)
    return registered_aliases


def _iter_candidate_paths(
    source: str,
    base_dir: Path | None,
    project_root: Path,
) -> Iterable[Path]:
    """Yield candidate paths for a dataframe source."""

    # Treat explicit file paths first (absolute or relative with separators / extension)
    if _looks_like_path(source):
        path = Path(source)
        if not path.is_absolute():
            path = (project_root / path).resolve()

        yield path
        if path.exists():
            return

        # If the explicit path doesn't exist, fall back to basename matching.
        # e.g. absolute local paths that don't exist in the container.
        if path.name:
            source = path.name
        else:
            source = str(path)

    if base_dir is None:
        return

    candidates: list[str] = []

    def append_unique(value: str) -> None:
        if value and value not in candidates:
            candidates.append(value)

    append_unique(source)
    append_unique(source.lower())
    append_unique(source.capitalize())

    parts = [part for part in re.split(r"[_\\s]+", source) if part]
    if parts:
        append_unique("_".join(word.capitalize() for word in parts))
        append_unique("".join(word.capitalize() for word in parts))

    # Ensure .parquet variants exist
    for variant in list(candidates):
        if not variant.endswith(".parquet"):
            append_unique(f"{variant}.parquet")

    # Allow _polars suffixed files (current production naming convention)
    polars_variants = []
    for variant in list(candidates):
        stem = variant[:-8] if variant.endswith(".parquet") else variant
        if stem.endswith("_polars"):
            continue
        polars_variants.append(f"{stem}_polars")
        polars_variants.append(f"{stem}_polars.parquet")

    for variant in polars_variants:
        append_unique(variant)

    for variant in candidates:
        yield base_dir / variant


def _looks_like_path(source: str) -> bool:
    """Return ``True`` if *source* is likely a filesystem path."""
    return (
        source.endswith(".parquet")
        or "/" in source
        or "\\" in source
    )


def _read_parquet_if_exists(
    path: Path,
    logical_name: str,
    logger: logging.Logger,
    dataframe_format: str,
) -> Any | None:
    """Attempt to load a Parquet file (or directory) at *path*."""

    try:
        if not path.exists():
            return None

        if path.is_dir():
            pattern = str(path / "*.parquet")
            if dataframe_format == "pandas":
                return pd.read_parquet(pattern)
            return pl.read_parquet(pattern)

        if dataframe_format == "pandas":
            return pd.read_parquet(path)
        return pl.read_parquet(path)
    except Exception as exc:  # pragma: no cover - runtime filesystem issues
        logger.warning(
            "Failed to load dataframe '%s' from %s: %s",
            logical_name,
            path,
            exc,
        )
        return None


def _is_database_source(source: str) -> bool:
    """Return True if the logical name references a database URL."""

    if not source:
        return False
    prefix = source.split("#", 1)[0].lower()
    return prefix.startswith("postgresql://") or prefix.startswith("postgres://") or prefix.startswith("postgresql+")


def _load_database_table(source: str, dataframe_format: str, logger: logging.Logger) -> Any | None:
    """Load a SQL table defined as ``<url>#<schema.table>`` into a dataframe."""

    if "#" not in source:
        logger.warning("Database source is missing table name: %s", source)
        return None

    db_url, table_spec = source.split("#", 1)
    db_url = db_url.strip()
    table_spec = table_spec.strip()
    if not db_url or not table_spec:
        logger.warning("Database source must include both URL and table name: %s", source)
        return None

    sync_url = _coerce_sync_db_url(db_url)
    if not sync_url:
        logger.warning("Unsupported database URL: %s", db_url)
        return None

    schema, table_name = _parse_table_spec(table_spec)
    if not table_name:
        logger.warning("Database table name is empty for source: %s", source)
        return None

    select_sql = _build_table_query(schema, table_name)

    try:
        engine = create_engine(sync_url, pool_pre_ping=True, future=True)
    except Exception as exc:
        logger.warning("Could not create database engine for %s: %s", sync_url, exc)
        return None

    try:
        with engine.connect() as connection:
            frame = pd.read_sql_query(text(select_sql), connection)
    except SQLAlchemyError as exc:
        logger.warning("Unable to load table '%s' from %s: %s", table_spec, sync_url, exc)
        return None
    finally:
        try:
            engine.dispose()
        except Exception:
            pass

    frame = _coerce_polars_compatible_types(frame)
    if dataframe_format == "polars":
        return pl.from_pandas(frame)
    return frame


def _coerce_sync_db_url(url: str) -> str | None:
    """Convert async URLs to synchronous ones supported by pandas/SQLAlchemy."""

    trimmed = url.strip()
    if not trimmed:
        return None
    if "+asyncpg" in trimmed:
        return trimmed.replace("+asyncpg", "+psycopg2", 1)
    if trimmed.startswith("postgres://"):
        return "postgresql+psycopg2://" + trimmed[len("postgres://") :]
    if trimmed.startswith("postgresql://") and "+psycopg2" not in trimmed:
        return trimmed.replace("postgresql://", "postgresql+psycopg2://", 1)
    return trimmed


def _parse_table_spec(spec: str) -> tuple[str | None, str]:
    cleaned = spec.strip().strip('"')
    if not cleaned:
        return None, ""
    if "." in cleaned:
        schema, table = cleaned.split(".", 1)
        return schema.strip().strip('"'), table.strip().strip('"')
    return None, cleaned


def _quote_identifier(identifier: str) -> str:
    safe = identifier.replace('"', '""')
    return f'"{safe}"'


def _build_table_query(schema: str | None, table: str) -> str:
    table_ident = _quote_identifier(table)
    if schema:
        schema_ident = _quote_identifier(schema)
        return f"SELECT * FROM {schema_ident}.{table_ident}"
    return f"SELECT * FROM {table_ident}"


def _coerce_polars_compatible_types(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert unsupported pandas object columns (e.g., UUID) to strings."""

    if frame.empty:
        return frame

    for column in frame.columns:
        series = frame[column]
        if series.dtype == "object":
            if series.map(_is_uuid_value).any():
                frame[column] = series.astype(str)
    return frame


def _is_uuid_value(value: Any) -> bool:
    return isinstance(value, uuid.UUID)


def _register_dataframe(
    agent: Any,
    logical_name: str,
    dataframe: Any,
    registry: dict[str, Any],
) -> None:
    """Register dataframe in the agent under several aliases."""

    aliases: set[str] = set()
    aliases.add(logical_name)

    if "#" in logical_name:
        table_spec = logical_name.split("#", 1)[1]
        clean_table = re.sub(r"\W+", "_", table_spec).strip("_")
        if clean_table:
            aliases.add(clean_table)
            aliases.add(clean_table.lower())

    path = Path(logical_name)
    if path.name:
        aliases.add(path.name)
        aliases.add(path.stem)
        aliases.add(path.stem.lower())

    sanitized = re.sub(r"\W+", "_", logical_name).strip("_")
    if sanitized:
        aliases.add(sanitized)
        aliases.add(sanitized.lower())

    for alias in aliases:
        if not alias or alias in registry:
            continue
        agent.execution_functions[alias] = dataframe
        agent.execution_runtime.system_bindings[alias] = dataframe
        agent.execution_globals[alias] = dataframe
        registry[alias] = dataframe


def _publish_dataframe_registry(agent: Any, registry: dict[str, Any]) -> None:
    """Expose the dataframe registry to the runtime for exploration code."""

    if not registry:
        return

    for name in ("loaded_dataframes", "_loaded_dataframes"):
        agent.execution_functions[name] = registry
        agent.execution_runtime.system_bindings[name] = registry
        agent.execution_globals[name] = registry


def _apply_preprocessing(
    *,
    agent: Any,
    logical_name: str,
    dataframe: Any,
    dataframe_format: str,
    project_root: Path,
    logger: logging.Logger,
) -> Any:
    """Apply configured preprocessing operations to the loaded dataframe."""
    config = getattr(agent, "config", None)
    if config is None:
        return dataframe

    operations = config.get_preprocessors_for(logical_name)
    if not operations:
        return dataframe

    if dataframe_format != "pandas":
        logger.warning(
            "Skipping preprocessors for '%s' (format '%s' not yet supported).",
            logical_name,
            dataframe_format,
        )
        return dataframe

    repo_path = str(project_root)

    for operation in operations:
        logger.info("Applying preprocessor '%s' to dataframe '%s'", operation.name, logical_name)

        globals_map: dict[str, Any] = {
            "df": dataframe,
            "pd": pd,
            "pl": pl,
        }

        success, updated_globals, logs = sync_execute_catch_logs_errors(
            operation.code,
            globals_map,
            repo_path=repo_path,
        )

        if not success:
            logger.error(
                "Preprocessor '%s' failed for dataframe '%s'. Logs:\n%s",
                operation.name,
                logical_name,
                logs,
            )
            continue

        candidate = updated_globals.get("df")
        if candidate is None and "result" in updated_globals:
            candidate = updated_globals["result"]

        if not isinstance(candidate, pd.DataFrame):
            logger.warning(
                "Preprocessor '%s' did not return a pandas DataFrame; skipping its result.",
                operation.name,
            )
            continue

        dataframe = candidate

    return dataframe


def _load_single_dataframe(
    source: str,
    default_base_dir: Path | None,
    project_root: Path,
    logger: logging.Logger,
    dataframe_format: str,
    extra_candidates: list[str] | None = None,
) -> Any | None:
    """Return dataframe for the given *source* or ``None`` if unavailable."""

    source = _maybe_localize_demo_host(source)

    if _is_database_source(source):
        dataframe = _load_database_table(source, dataframe_format, logger)
        if dataframe is not None:
            return dataframe
        logger.warning("Failed to load database source '%s'", source)
        return None

    tried: set[Path] = set()

    def _normalized_path(path_str: str) -> Path:
        expanded = os.path.expandvars(os.path.expanduser(path_str))
        path = Path(expanded)
        if not path.is_absolute():
            path = (project_root / expanded).resolve()
        return path

    candidate_paths: list[Path] = []

    if extra_candidates:
        for raw_candidate in extra_candidates:
            if not raw_candidate:
                continue
            path = _normalized_path(raw_candidate)
            if path not in tried:
                candidate_paths.append(path)
                tried.add(path)

    for candidate in _iter_candidate_paths(source, default_base_dir, project_root):
        if candidate not in tried:
            candidate_paths.append(candidate)
            tried.add(candidate)

    for candidate in candidate_paths:
        dataframe = _read_parquet_if_exists(candidate, source, logger, dataframe_format)
        if dataframe is not None:
            return dataframe

    logger.warning("Could not locate dataframe '%s'", source)
    return None


def _iter_candidate_paths(
    source: str,
    base_dir: Path | None,
    project_root: Path,
) -> Iterable[Path]:
    """Yield candidate paths for a dataframe source."""

    if _looks_like_path(source):
        path = Path(source)
        if not path.is_absolute():
            path = (project_root / path).resolve()

        yield path
        if path.exists():
            return

        # If the explicit path does not exist (common when configs contain
        # machine-specific roots), fall back to basename matching.
        if path.name:
            source = path.name
        else:
            source = str(path)

    if base_dir is None:
        return

    candidates: list[str] = []

    def append_unique(value: str) -> None:
        if value and value not in candidates:
            candidates.append(value)

    append_unique(source)
    append_unique(source.lower())
    append_unique(source.capitalize())

    parts = [part for part in re.split(r"[_\\s]+", source) if part]
    if parts:
        append_unique("_".join(word.capitalize() for word in parts))
        append_unique("".join(word.capitalize() for word in parts))

    for variant in list(candidates):
        if not variant.endswith(".parquet"):
            append_unique(f"{variant}.parquet")

    # Production syncer writes *_polars.parquet files; make sure we consider
    # those alongside canonical logical names.
    polars_variants: list[str] = []
    for variant in list(candidates):
        stem = variant[:-8] if variant.endswith(".parquet") else variant
        if stem.endswith("_polars"):
            continue
        polars_variants.append(f"{stem}_polars")
        polars_variants.append(f"{stem}_polars.parquet")

    for variant in polars_variants:
        append_unique(variant)

    for variant in candidates:
        yield base_dir / variant


def _looks_like_path(source: str) -> bool:
    """Return ``True`` if *source* is likely a filesystem path."""
    return source.endswith(".parquet") or "/" in source or "\\" in source


def _read_parquet_if_exists(
    path: Path,
    logical_name: str,
    logger: logging.Logger,
    dataframe_format: str,
) -> Any | None:
    """Attempt to load a Parquet file (or directory) at *path*."""

    try:
        if not path.exists():
            return None

        if path.is_dir():
            pattern = str(path / "*.parquet")
            if dataframe_format == "pandas":
                return pd.read_parquet(pattern)
            return pl.read_parquet(pattern)

        if dataframe_format == "pandas":
            return pd.read_parquet(path)
        return pl.read_parquet(path)
    except Exception as exc:  # pragma: no cover - runtime issues
        logger.warning(
            "Failed to load dataframe '%s' from %s: %s",
            logical_name,
            path,
            exc,
        )
        return None
IN_DOCKER = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER") == "true"
DEMO_DB_EXTERNAL_HOST = os.environ.get("FAST_AGENT_DEMO_DB_EXTERNAL_HOST", "37.27.67.52")
DEMO_DB_INTERNAL_HOST = os.environ.get("FAST_AGENT_DEMO_DB_INTERNAL_HOST", "172.17.0.3")
def _maybe_localize_demo_host(source: str) -> str:
    """
    Replace public Adventure Works host with the internal Docker host when needed.
    """
    if DEMO_DB_EXTERNAL_HOST not in source:
        return source

    running_locally = server_config.ENVIRONMENT == "local" and not IN_DOCKER
    if running_locally:
        return source

    return source.replace(DEMO_DB_EXTERNAL_HOST, DEMO_DB_INTERNAL_HOST)
