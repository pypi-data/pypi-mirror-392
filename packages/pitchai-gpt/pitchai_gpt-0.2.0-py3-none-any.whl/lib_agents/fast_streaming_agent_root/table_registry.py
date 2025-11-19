"""Utility helpers for registering pandas tables during agent execution."""

from __future__ import annotations

from typing import Any, Callable

import pandas as pd


class TableRegistry:
    """In-memory storage for tables that can be collected by the UI."""

    def __init__(self) -> None:
        self._tables: dict[str, pd.DataFrame] = {}

    @staticmethod
    def _coerce_to_pandas(value: Any) -> pd.DataFrame | None:
        if value is None:
            return None
        if isinstance(value, pd.DataFrame):
            return value.copy()

        try:
            import polars as pl  # type: ignore

            if isinstance(value, pl.DataFrame):
                return value.to_pandas()
        except ModuleNotFoundError:
            pass
        except Exception:
            return None

        if hasattr(value, "to_pandas"):
            try:
                converted = value.to_pandas()
                if isinstance(converted, pd.DataFrame):
                    return converted
            except Exception:
                return None
        return None

    def register(self, variable_name: str, table: Any) -> pd.DataFrame:
        key = variable_name.strip()
        if not key:
            raise ValueError("Table variable name must be a non-empty string.")

        frame = self._coerce_to_pandas(table)
        if frame is None:
            raise TypeError(f"Object for '{variable_name}' is not convertible to pandas DataFrame.")

        self._tables[key] = frame
        return frame

    def get(self, variable_name: str) -> pd.DataFrame | None:
        key = variable_name.strip()
        return self._tables.get(key)

    def resolve(
        self,
        variable_name: str,
        lookup: Callable[[str], Any] | None = None,
    ) -> pd.DataFrame | None:
        table = self.get(variable_name)
        if table is not None:
            return table

        if lookup is None:
            return None

        raw_value = lookup(variable_name)
        frame = self._coerce_to_pandas(raw_value)
        if frame is not None:
            self._tables[variable_name.strip()] = frame
        return frame
