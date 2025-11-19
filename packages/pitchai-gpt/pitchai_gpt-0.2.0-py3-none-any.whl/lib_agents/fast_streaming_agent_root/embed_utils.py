"""Utilities for processing <embed> tags in final answers."""

from __future__ import annotations

import html
import re
from typing import Any

import pandas as pd


EMBED_PATTERN = re.compile(
    r"<embed>\s*\{?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}?\s*</embed>"
)


def _render_dataframe(df: pd.DataFrame, title: str) -> str:
    table_html = df.to_html(index=False, border=0)
    table_html = table_html.replace(
        "<table>",
        "<table style=\"width:100%;border-collapse:collapse;font-size:0.9rem;\">",
    )
    table_html = table_html.replace(
        "<th>",
        "<th style=\"text-align:left;padding:0.5rem;border-bottom:1px solid #E5E7EB;color:#344054;font-weight:600;\">",
    )
    table_html = table_html.replace(
        "<td>",
        "<td style=\"padding:0.5rem;border-bottom:1px solid #F2F4F7;color:#101828;\">",
    )
    return (
        '<div class="embedded-table" '
        'style="margin:1.25rem 0;padding:0;border:1px solid #E5E7EB;'
        'border-radius:0.75rem;box-shadow:0 1px 2px rgba(16,24,40,0.08);overflow-x:auto;background:#fff;">'
        f"<div style=\"padding:0.5rem 1rem;font-size:0.75rem;font-weight:600;color:#475467;border-bottom:1px solid #E5E7EB;\">{html.escape(title)}</div>"
        f"<div style=\"padding:1rem;\">{table_html}</div>"
        "</div>"
    )


def replace_embed_tags(agent: Any, text: str) -> str:
    """Replace `<embed>` tags within *text* using tables available to *agent*."""

    if "<embed>" not in text:
        return text

    matches = list(EMBED_PATTERN.finditer(text))
    if not matches:
        return text

    processed = text
    for match in matches:
        variable = match.group(1)
        placeholder = match.group(0)
        table = None
        try:
            if hasattr(agent, "resolve_table"):
                table = agent.resolve_table(variable)
            elif hasattr(agent, "table_registry"):
                table = agent.table_registry.resolve(variable)  # type: ignore[attr-defined]
        except Exception:
            table = None

        if table is not None:
            if not isinstance(table, pd.DataFrame):
                table = pd.DataFrame(table)
            replacement = _render_dataframe(table, variable)
        else:
            replacement = (
                '<div style="margin:0.75rem 0;padding:0.625rem 0.75rem;'
                'font-size:0.85rem;border-radius:0.5rem;border:1px solid #FCD34D;'
                'background:#FFFBEB;color:#92400E;">'
                f"⚠️ Kon tabel '{html.escape(variable)}' niet vinden in deze analyse."
                "</div>"
            )

        processed = processed.replace(placeholder, replacement, 1)

    return processed
