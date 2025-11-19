"""Helpers for detecting dataset usage while streaming LLM output."""

from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict
import re

from lib_agents.gpt.gpt import StreamObserver


@dataclass(frozen=True)
class DatasetInfo:
    """Metadata describing a dataframe or semantic layer referenced in code."""

    dataset_id: str
    display_name: str
    source_type: str  # e.g. "base" or "semantic"
    description: str | None = None


def generate_aliases(name: str) -> set[str]:
    """Generate common alias variants for a dataframe/semantic layer name."""

    aliases: set[str] = set()
    if not name:
        return aliases

    aliases.add(name)
    aliases.add(name.lower())

    path = Path(name)
    if path.name:
        aliases.add(path.name)
        aliases.add(path.name.lower())
    if path.stem:
        aliases.add(path.stem)
        aliases.add(path.stem.lower())

    sanitized = re.sub(r"\W+", "_", name).strip("_")
    if sanitized:
        aliases.add(sanitized)
        aliases.add(sanitized.lower())

    return aliases


class DatasetUsageObserver(StreamObserver):
    """Observes streamed chunks and emits events when known datasets appear in code blocks."""

    def __init__(
        self,
        alias_map: Dict[str, DatasetInfo],
        callback: Callable[[DatasetInfo], Awaitable[None] | None],
        *,
        max_events: int = 25,
    ) -> None:
        self._patterns: Dict[str, tuple[DatasetInfo, re.Pattern[str]]] = {
            alias: (info, re.compile(rf"\b{re.escape(alias)}\b"))
            for alias, info in alias_map.items()
        }
        self._callback = callback
        self._in_code_block = False
        self._reported_ids: set[str] = set()
        self._max_events = max_events
        self._events = 0

    async def on_text(self, text: str) -> None:
        if not text or not self._patterns or self._events >= self._max_events:
            return

        segments = text.split("```")
        for idx, segment in enumerate(segments):
            if self._in_code_block and self._events < self._max_events:
                await self._process_code_segment(segment)
            if idx != len(segments) - 1:
                self._in_code_block = not self._in_code_block

    async def _process_code_segment(self, segment: str) -> None:
        lower_segment = segment.lower()
        for alias, (info, pattern) in self._patterns.items():
            if self._events >= self._max_events:
                return
            if info.dataset_id in self._reported_ids:
                continue
            if pattern.search(lower_segment):
                result = self._callback(info)
                if asyncio.iscoroutine(result) or inspect.isawaitable(result):  # pragma: no cover - convenience
                    await result
                self._reported_ids.add(info.dataset_id)
                self._events += 1
