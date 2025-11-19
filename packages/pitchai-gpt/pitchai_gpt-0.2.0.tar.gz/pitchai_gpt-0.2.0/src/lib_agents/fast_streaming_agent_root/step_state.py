"""Step container state tracking for FastStreamingAgent streaming."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class StepContainerState:
    """Tracks state for step container UI during streaming."""

    assistant_content: str = ""
    processed_blocks: int = 0
    in_code_block: bool = False
    buffer: str = ""
    buffering: bool = False
    problematic_languages: list[str] = field(default_factory=lambda: [
        "tool_code", "tool_call", "tool_code>", "tool_call>",
        "<execute_python>", "<execute_bash>"
    ])
    token_usage: Optional[object] = None

    # Tool-call execution metadata (only used in tool mode)
    tool_call_id: Optional[str] = None
    tool_call_name: Optional[str] = None
    tool_call_arguments: str = ""
    tool_call_args_dict: Optional[dict] = None
    tool_call_payload: Optional[dict] = None

    step_reasoning_shown: bool = False
    step_reasoning_buffer: str = ""
    step_ids_set: bool = False
    step_container_sent: bool = False
    step_id: Optional[str] = None
    reasoning_id: Optional[str] = None
    title_dutch_id: Optional[str] = None
    badge_id: Optional[str] = None
    code_id: Optional[str] = None
    output_id: Optional[str] = None
    reasoning_container_id: Optional[str] = None
    code_container_id: Optional[str] = None
    output_container_id: Optional[str] = None


@dataclass
class CodeBlockLog:
    """Tracks information about a single code block execution."""

    language: str
    code: str
    execution_time: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    output: str = ""
    had_error: bool = False
    stop_blocked: bool = False
    token_stats: Optional[dict] = None


@dataclass
class StepLog:
    """Tracks information about a single agent step."""

    step_number: int
    start_time: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    reasoning: str = ""
    code_blocks: list = field(default_factory=list)
    full_response: str = ""
    end_time: Optional[str] = None
    token_usage: Optional[dict] = None
