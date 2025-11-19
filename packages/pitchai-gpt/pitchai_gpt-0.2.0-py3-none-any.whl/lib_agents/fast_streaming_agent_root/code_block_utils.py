"""Utilities for detecting and formatting streamed code blocks."""

from __future__ import annotations

import re
from typing import List, Tuple

from .colors import Colors

# Precompiled patterns used when scanning streamed content
CODE_FENCE_PATTERN = re.compile(r"```(\w*)\n(.*?)\n```", re.DOTALL)
PARTIAL_CODE_PATTERN = re.compile(r"```(\w*)\n(.*?)$", re.DOTALL)


def detect_complete_code_blocks(text: str) -> List[Tuple[str, str, int, int]]:
    """Return all complete code fences inside *text*.

    Args:
        text: Streamed content that may contain Markdown code fences.

    Returns:
        A list of tuples containing the code snippet, declared language and the
        start/end positions within the text.
    """
    blocks: List[Tuple[str, str, int, int]] = []
    for match in CODE_FENCE_PATTERN.finditer(text):
        language = (match.group(1) or "").strip()
        code = match.group(2)

        # Some model responses stream as ```\n```python\n... which confuses the
        # primary fence matcher. Normalise by removing the redundant inner fence
        # and capturing the intended language.
        nested_fence = re.match(r"^\s*```(\w+)\n", code)
        if nested_fence:
            # Promote the nested language declaration when the outer fence omitted it
            if not language:
                language = nested_fence.group(1)
            code = code[nested_fence.end():]

        # Defensive cleanup when models accidentally leave an unmatched fence fragment.
        code = re.sub(r"\n```$", "", code)
        language = language or "python"

        start = match.start()
        end = match.end()
        blocks.append((code, language, start, end))
    return blocks


def has_partial_code_block(text: str) -> bool:
    """Return True when *text* ends with an incomplete Markdown code fence."""
    return bool(PARTIAL_CODE_PATTERN.search(text))


def apply_colors(content: str, in_code_block: bool) -> str:
    """Apply terminal colors so code fences remain readable while streaming."""
    colored_content = content
    if "```" in content:
        if not in_code_block:
            # Starting a code block - apply cyan color
            colored_content = content.replace("```", f"{Colors.CYAN}```{Colors.RESET}")
        else:
            # Ending a code block - reset color
            colored_content = content.replace("```", f"```{Colors.RESET}")
    elif in_code_block:
        # Inside code block - keep cyan
        colored_content = f"{Colors.CYAN}{content}{Colors.RESET}"
    return colored_content
