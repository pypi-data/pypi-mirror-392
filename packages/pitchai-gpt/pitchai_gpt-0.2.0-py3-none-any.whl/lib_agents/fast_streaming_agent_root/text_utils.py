"""Utility helpers for processing markdown-like text responses."""

from __future__ import annotations

def strip_code_fence(text: str | None) -> str:
    """Return *text* without surrounding Markdown code fences."""
    if not text:
        return ""
    value = text.strip()
    if not value.startswith("```"):
        return value
    closing = value.rfind("```")
    if closing <= 0:
        return value
    body = value[3:closing].lstrip("\n")
    if "\n" in body:
        first_line, rest = body.split("\n", 1)
        candidate = first_line.strip()
        if candidate and " " not in candidate and len(candidate) <= 20:
            body = rest
        else:
            body = first_line + "\n" + rest
    body = body.strip("\n").strip()
    return body or value
