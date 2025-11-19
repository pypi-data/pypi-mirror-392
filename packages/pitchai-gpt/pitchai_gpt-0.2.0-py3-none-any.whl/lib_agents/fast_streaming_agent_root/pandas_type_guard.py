"""Runtime patches that make pandas a bit more forgiving for the agent."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_string_dtype

_ORIGINAL_SERIES_EQ = pd.Series.eq
_ORIGINAL_SERIES_DUNDER_EQ = pd.Series.__eq__
_ORIGINAL_SERIES_ISIN = pd.Series.isin
_ORIGINAL_DATAFRAME_MERGE = pd.DataFrame.merge

_WARN_CACHE: set[str] = set()


def _format_series_name(series: pd.Series) -> str:
    name = getattr(series, "name", None)
    return "<unnamed series>" if name is None else str(name)


def _should_treat_as_iterable(values: Any) -> bool:
    if isinstance(values, (str, bytes)):
        return False
    return isinstance(values, Iterable)


def _is_scalar_missing(value: Any) -> bool:
    if _should_treat_as_iterable(value):
        return False
    return pd.isna(value)  # type: ignore[arg-type]


def _emit_warning(message: str) -> None:
    if message not in _WARN_CACHE:
        _WARN_CACHE.add(message)
        print(message)


def _coerce_value_with_warning(
    series: pd.Series,
    other: Any,
) -> tuple[Any, bool, bool]:
    if _is_scalar_missing(other):
        message = (
            f"[pandas dtype guard] Equality comparison against missing values on column "
            f"'{_format_series_name(series)}' always returns False; use .isna()/.notna()."
        )
        _emit_warning(message)
        return other, False, True

    converted = other
    issued_warning = False

    if is_string_dtype(series.dtype) or series.dtype == object:
        if isinstance(other, (int, float)) and not isinstance(other, bool):
            converted = str(other)
            issued_warning = True
    elif is_numeric_dtype(series.dtype) and isinstance(other, str):
        try:
            converted = pd.to_numeric(pd.Series([other])).iloc[0]
        except Exception:
            pass

    return converted, issued_warning, False


def _series_eq_with_type_warning(
    self: pd.Series,
    other: Any,
    *args: Any,
    **kwargs: Any,
) -> pd.Series:
    converted_other, issued_warning, _ = _coerce_value_with_warning(self, other)
    if issued_warning:
        message = (
            f"[pandas dtype guard] Column '{_format_series_name(self)}' stores text values but was compared "
            f"with numeric value {other!r}; coercing the lookup to {converted_other!r} to avoid "
            "accidentally dropping all matches."
        )
        _emit_warning(message)
    return _ORIGINAL_SERIES_EQ(self, converted_other, *args, **kwargs)


def _series_dunder_eq_with_type_warning(self: pd.Series, other: Any) -> pd.Series:
    converted_other, issued_warning, _ = _coerce_value_with_warning(self, other)
    if issued_warning:
        message = (
            f"[pandas dtype guard] Column '{_format_series_name(self)}' stores text values but was compared "
            f"with numeric value {other!r}; coercing the lookup to {converted_other!r} to avoid "
            "accidentally dropping all matches."
        )
        _emit_warning(message)
    return _ORIGINAL_SERIES_DUNDER_EQ(self, converted_other)


def _convert_values_to_strings(values: Any) -> Any:
    def _to_str(v: Any) -> Any:
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return str(v)
        return v

    if isinstance(values, pd.Series):
        return values.astype(str)
    if isinstance(values, pd.Index):
        return pd.Index([_to_str(v) for v in values])
    if isinstance(values, np.ndarray):
        return np.array([_to_str(v) for v in values], dtype=object)
    if isinstance(values, tuple):
        return tuple(_to_str(v) for v in values)
    if isinstance(values, frozenset):
        return frozenset(_to_str(v) for v in values)
    if isinstance(values, set):
        return {_to_str(v) for v in values}
    if isinstance(values, list):
        return [_to_str(v) for v in values]
    return values


def _series_isin_with_type_warning(
    self: pd.Series,
    values: Any,
    *args: Any,
    **kwargs: Any,
) -> pd.Series:
    converted_values = values
    if _should_treat_as_iterable(values) and (is_string_dtype(self.dtype) or self.dtype == object):
        if any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
            converted_values = _convert_values_to_strings(values)
            message = (
                f"[pandas dtype guard] Column '{_format_series_name(self)}' stores text values but isin lookup "
                "contains numeric values; coercing lookup values to strings."
            )
            _emit_warning(message)
    return _ORIGINAL_SERIES_ISIN(self, converted_values, *args, **kwargs)


def _coerce_merge_key_to_string(dataset: pd.DataFrame, col: str) -> pd.DataFrame:
    if dataset[col].dtype == object or is_string_dtype(dataset[col].dtype):
        return dataset
    copy = dataset.copy()
    copy[col] = copy[col].astype(str)
    return copy


def _dataframe_merge_with_type_warning(
    self: pd.DataFrame,
    right: pd.DataFrame,
    *args: Any,
    **kwargs: Any,
) -> pd.DataFrame:
    on = kwargs.get("on")
    left_on = kwargs.get("left_on")
    right_on = kwargs.get("right_on")

    def _ensure_list(value: Any | None) -> list[str] | None:
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            return list(value)
        return [value]

    if on is not None:
        left_keys = right_keys = _ensure_list(on)
    else:
        left_keys = _ensure_list(left_on)
        right_keys = _ensure_list(right_on)
        if left_keys is None and right_keys is None:
            common = list(set(self.columns) & set(right.columns))
            left_keys = right_keys = common

    if not left_keys or not right_keys:
        return _ORIGINAL_DATAFRAME_MERGE(self, right, *args, **kwargs)

    left_df = self
    right_df = right

    # Align key lists in length
    while len(right_keys) < len(left_keys):
        right_keys.append(right_keys[-1])
    while len(left_keys) < len(right_keys):
        left_keys.append(left_keys[-1])

    for left_key, right_key in zip(left_keys, right_keys, strict=False):
        if left_key not in left_df.columns or right_key not in right_df.columns:
            continue

        left_series = left_df[left_key]
        right_series = right_df[right_key]

        left_text = is_string_dtype(left_series.dtype) or left_series.dtype == object
        right_text = is_string_dtype(right_series.dtype) or right_series.dtype == object

        if left_text and not right_text:
            right_df = _coerce_merge_key_to_string(right_df, right_key)
            message = (
                f"[pandas dtype guard] Merge key '{left_key}' is text on the left but numeric on the right; "
                "coercing right key to string."
            )
            _emit_warning(message)
        elif right_text and not left_text:
            left_df = _coerce_merge_key_to_string(left_df, left_key)
            message = (
                f"[pandas dtype guard] Merge key '{left_key}' is numeric on the left but text on the right; "
                "coercing left key to string."
            )
            _emit_warning(message)

    return _ORIGINAL_DATAFRAME_MERGE(left_df, right_df, *args, **kwargs)


if pd.Series.eq is not _series_eq_with_type_warning:
    pd.Series.eq = _series_eq_with_type_warning
if pd.Series.__eq__ is not _series_dunder_eq_with_type_warning:
    pd.Series.__eq__ = _series_dunder_eq_with_type_warning
if pd.Series.isin is not _series_isin_with_type_warning:
    pd.Series.isin = _series_isin_with_type_warning
if pd.DataFrame.merge is not _dataframe_merge_with_type_warning:
    pd.DataFrame.merge = _dataframe_merge_with_type_warning
