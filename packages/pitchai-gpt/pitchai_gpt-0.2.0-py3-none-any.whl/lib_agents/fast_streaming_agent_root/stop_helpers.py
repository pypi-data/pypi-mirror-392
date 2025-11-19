"""Stop signal detection and phase transition helpers for FastStreamingAgent.

This module contains functions for detecting when the agent should stop
its current phase and transition to the next phase of execution.
"""

import logging
import re
from typing import Any, TYPE_CHECKING

from .colors import Colors

if TYPE_CHECKING:
    from .main import RequestContext

LOGGER = logging.getLogger(__name__)


def should_stop(
    agent: Any,
    iteration: int,
    assistant_response: str,
    had_error: bool,
    has_code_output: bool
) -> tuple[bool, str]:
    """Detect if the agent should stop based on various signals.

    Args:
        agent: The agent instance
        iteration: Current iteration number
        assistant_response: The assistant's response text
        had_error: Whether an error occurred
        has_code_output: Whether code output was produced

    Returns:
        Tuple of (should_stop, stop_reason)
    """
    has_code_blocks = "```" in assistant_response
    is_text_only_response = not has_code_blocks and not has_code_output
    is_empty_response = len(assistant_response.strip()) == 0

    agent.logger.debug(
        "STOP DEBUG: iteration=%s, has_code_blocks=%s, has_code_output=%s, is_text_only=%s, had_error=%s",
        iteration + 1,
        has_code_blocks,
        has_code_output,
        is_text_only_response,
        had_error,
    )
    agent.logger.debug(
        "STOP DEBUG: response_length=%s, response_preview=%s",
        len(assistant_response),
        assistant_response[:200],
    )

    if agent.request_context.name == "FINAL_ANSWER" and is_text_only_response and not had_error:
        print("[STOP_HELPERS] FINAL ANSWER text-only")
        return True, "final_answer_text_only"

    if is_text_only_response and not is_empty_response and not had_error:
        if not hasattr(agent, "consecutive_text_responses"):
            agent.consecutive_text_responses = 0
        agent.consecutive_text_responses += 1
        print("[STOP_HELPERS] text-only response", agent.consecutive_text_responses, agent.request_context.name)
    else:
        agent.consecutive_text_responses = 0

    stop = False
    reason = ""

    if agent.stop_requested:
        stop = True
        reason = "stop() function called"
    elif is_empty_response and agent.request_context.name != "DETAIL" and not has_code_output:
        stop = True
        reason = "empty response"
    elif is_text_only_response and not had_error and agent.request_context.name != "FINAL_ANSWER":
        stop = True
        reason = "text-only response"
    elif hasattr(agent, "consecutive_text_responses") and agent.consecutive_text_responses >= 2:
        stop = True
        reason = f"{agent.consecutive_text_responses} consecutive text-only responses"

    return stop, reason


def stop_or_next_phase(
    agent: Any,
    assistant_response: str,
    should_stop: bool,
    stop_reason: str
) -> None:
    """Handle stop signals and transition to next phase based on context.

    Args:
        agent: The agent instance
        assistant_response: The assistant's response text
        should_stop: Whether a stop signal was detected
        stop_reason: The reason for stopping
    """
    if should_stop:
        agent.logger.info("%s[Stop Signal: %s]%s", Colors.YELLOW, stop_reason, Colors.RESET)
        agent.logger.info("%s[Request Context: %s]%s", Colors.YELLOW, agent.request_context.value, Colors.RESET)

        if agent.request_context.name == "FOLLOW_UP":
            agent.logger.info("%s[Follow-up: Using last response as final answer]%s", Colors.GREEN, Colors.RESET)

            final_text = re.sub(r"```.*?```", "", assistant_response, flags=re.DOTALL).strip()

            agent.final_answer_requested = True
            agent.waiting_for_final_answer = True
            agent.detail_requested = True

            agent.final_answer_accumulator = [final_text or assistant_response]

        elif agent.request_context.name in ["INITIAL", "DETAIL"]:
            agent.stop_requested = True
            agent.stop_summary = f"Stopped: {stop_reason}"

        elif agent.request_context.name == "FINAL_ANSWER":
            pass
