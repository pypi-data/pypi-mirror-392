"""In-memory cache for preloaded dataframes and semantic layer materialisations.

This module allows the FastStreamingAgent runtime to reuse dataframes that were
loaded during application startup (e.g. container boot).  Agents can request a
fresh copy of the preloaded tables without re-reading Parquet files or
re-executing semantic-layer code.
"""

from __future__ import annotations

import threading
from dataclasses import replace
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

import pandas as pd

if TYPE_CHECKING:  # pragma: no cover - only for typing
    from .semantic_layer_runtime import SemanticLayerEntry

try:  # Optional dependency
    import polars as pl  # type: ignore
except ImportError:  # pragma: no cover - polars not installed
    pl = None  # type: ignore

# Enable copy-on-write so shallow pandas copies remain isolated
try:  # pandas >= 2.0
    pd.options.mode.copy_on_write = True  # type: ignore[attr-defined]
    _PANDAS_COW = True
except AttributeError:  # pragma: no cover - older pandas versions
    _PANDAS_COW = False

_LOCK = threading.RLock()
_BASE_STORE: Dict[str, Dict[str, Any]] = {}
_SEMANTIC_STORE: Dict[str, Dict[str, Any]] = {}

LOGGER = logging.getLogger(__name__)


def _normalise_key(config_path: str | Path | None) -> Optional[str]:
    if not config_path:
        return None
    try:
        return str(Path(config_path).resolve())
    except Exception:  # pragma: no cover - defensive
        return str(config_path)


def _copy_frame_for_store(frame: Any) -> Any:
    if isinstance(frame, pd.DataFrame):
        return frame.copy(deep=True)
    if pl is not None and isinstance(frame, pl.DataFrame):  # type: ignore[has-type]
        return frame.clone()
    return frame


def _copy_frame_for_use(frame: Any) -> Any:
    if isinstance(frame, pd.DataFrame):
        if _PANDAS_COW:
            return frame.copy(deep=False)
        return frame.copy(deep=True)
    if pl is not None and isinstance(frame, pl.DataFrame):  # type: ignore[has-type]
        return frame.clone()
    return frame


def _clone_entry(entry: Any, *, for_store: bool = False) -> Any:
    copier = _copy_frame_for_store if for_store else _copy_frame_for_use
    dataframe = copier(entry.dataframe)
    columns = [str(col) for col in getattr(dataframe, "columns", entry.columns)]
    row_count = int(getattr(dataframe, "shape", (entry.row_count,))[0])
    return replace(
        entry,
        dataframe=dataframe,
        columns=columns,
        row_count=row_count,
    )


def cache_preloaded_state(
    *,
    config_path: str | Path,
    dataframe_format: str,
    base_frames: Dict[str, Any],
    semantic_registry: Dict[str, Any],
) -> None:
    """Store pristine copies of base and semantic-layer dataframes."""
    key = _normalise_key(config_path)
    if key is None:
        return

    import os
    from threading import get_ident

    with _LOCK:
        _BASE_STORE[key] = {
            "format": dataframe_format,
            "frames": {name: _copy_frame_for_store(frame) for name, frame in base_frames.items()},
        }
        _SEMANTIC_STORE[key] = {name: _clone_entry(entry, for_store=True) for name, entry in semantic_registry.items()}
    LOGGER.info(
        "[%s] Cache updated for %s: base=%d semantic=%d pid=%s thread=%s store_size=%d store_id=%s",
        __name__,
        key,
        len(base_frames),
        len(semantic_registry),
        os.getpid(),
        get_ident(),
        len(_BASE_STORE),
        id(_BASE_STORE),
    )


def has_preloaded_state(config_path: str | Path | None) -> bool:
    key = _normalise_key(config_path)
    if key is None:
        return False
    import os
    from threading import get_ident
    with _LOCK:
        result = key in _BASE_STORE
    LOGGER.info(
        "[%s] has_preloaded_state(%s) -> %s pid=%s thread=%s store_size=%d store_id=%s keys=%s",
        __name__,
        key,
        result,
        os.getpid(),
        get_ident(),
        len(_BASE_STORE),
        id(_BASE_STORE),
        list(_BASE_STORE.keys()),
    )
    return result


def get_preloaded_base_dataframes(
    config_path: str | Path | None,
) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Return a fresh copy of preloaded base dataframes for the given config."""
    key = _normalise_key(config_path)
    if key is None:
        return None

    with _LOCK:
        payload = _BASE_STORE.get(key)
        if payload is None:
            return None
        dataframe_format = payload.get("format", "pandas")
        frames_ref = payload.get("frames", {})

    frames = {name: _copy_frame_for_use(frame) for name, frame in frames_ref.items()}
    return dataframe_format, frames


def get_preloaded_semantic_layers(
    config_path: str | Path | None,
) -> Optional[Dict[str, "SemanticLayerEntry"]]:
    """Return fresh copies of preloaded semantic-layer entries."""
    key = _normalise_key(config_path)
    if key is None:
        return None

    with _LOCK:
        registry = _SEMANTIC_STORE.get(key)
        if registry is None:
            return None
        snapshot = dict(registry)

    return {name: _clone_entry(entry) for name, entry in snapshot.items()}


def clear_preloaded_state(config_path: str | Path | None = None) -> None:
    """Remove cached state either for a specific config or entirely (tests)."""
    key = _normalise_key(config_path)
    import os
    from threading import get_ident
    with _LOCK:
        if key is None:
            _BASE_STORE.clear()
            _SEMANTIC_STORE.clear()
            LOGGER.info(
                "clear_preloaded_state(all) pid=%s thread=%s",
                os.getpid(),
                get_ident(),
            )
        else:
            _BASE_STORE.pop(key, None)
            _SEMANTIC_STORE.pop(key, None)
            LOGGER.info(
                "clear_preloaded_state(%s) pid=%s thread=%s",
                key,
                os.getpid(),
                get_ident(),
            )
