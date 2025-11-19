"""Token usage tracking and reporting helpers for FastStreamingAgent.

This module contains functions for tracking and displaying token usage
during agent execution.
"""

from typing import Any, TYPE_CHECKING, Union

from .colors import Colors

if TYPE_CHECKING:
    from .step_state import StepContainerState, StepLog


def update_total_token_usage(
    agent: Any,
    step_log: Union[dict, "StepLog"],
    state: "StepContainerState"
) -> tuple[int, int, int, int]:
    """Update agent's total token usage from step state.

    Args:
        agent: The agent instance
        step_log: The step log dictionary or StepLog dataclass to update
        state: The step container state with token usage

    Returns:
        Tuple of (prompt_tokens, completion_tokens, total_tokens, cached_tokens)
    """
    prompt_tokens = state.token_usage.prompt_tokens if hasattr(state.token_usage, "prompt_tokens") else 0
    completion_tokens = state.token_usage.completion_tokens if hasattr(state.token_usage, "completion_tokens") else 0
    total_tokens = state.token_usage.total_tokens if hasattr(state.token_usage, "total_tokens") else 0

    cached_tokens = 0
    if hasattr(state.token_usage, "prompt_tokens_details"):
        details = state.token_usage.prompt_tokens_details
        if hasattr(details, "cached_tokens"):
            cached_tokens = details.cached_tokens

    agent.total_tokens_used += total_tokens
    agent.total_cached_tokens += cached_tokens
    agent.total_prompt_tokens += prompt_tokens
    agent.total_completion_tokens += completion_tokens

    token_usage_data = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cached_tokens": cached_tokens
    }

    # Handle both dict and dataclass
    if hasattr(step_log, 'token_usage'):
        # StepLog dataclass
        step_log.token_usage = token_usage_data
    else:
        # Dictionary (legacy)
        step_log["token_usage"] = token_usage_data

    return prompt_tokens, completion_tokens, total_tokens, cached_tokens


def print_step_tokens_used(
    agent: Any,
    step_number: int,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    cached_tokens: int
) -> None:
    """Print token usage information for a step.

    Args:
        agent: The agent instance
        step_number: The step number
        prompt_tokens: Number of prompt tokens used
        completion_tokens: Number of completion tokens used
        total_tokens: Total tokens used
        cached_tokens: Number of cached tokens
    """
    agent._print_indented(f"\n{Colors.YELLOW}📊 Step {step_number} Token Usage:{Colors.RESET}")
    agent._print_indented(f"  • Prompt tokens: {prompt_tokens:,}")
    agent._print_indented(f"  • Completion tokens: {completion_tokens:,}")
    agent._print_indented(f"  • Total tokens: {total_tokens:,}")
    if cached_tokens > 0:
        cache_pct = cached_tokens * 100 // prompt_tokens if prompt_tokens > 0 else 0
        agent._print_indented(f"  • Cached tokens: {cached_tokens:,} ({cache_pct}% of prompt)")
    agent._print_indented(f"  • Running total: {agent.total_tokens_used:,} tokens")


def print_token_summary(agent: Any, iteration: int = 1) -> None:
    """Print final token usage summary for the entire conversation.

    Args:
        agent: The agent instance with token tracking
        iteration: The iteration count for averaging
    """
    if agent.total_tokens_used > 0:
        agent.logger.info("%s%s", Colors.GREEN, "=" * 50)
        agent.logger.info("🎯 FINAL TOKEN USAGE SUMMARY")
        agent.logger.info("%s%s%s", "=" * 50, Colors.RESET, "")
        agent.logger.info("  • Total prompt tokens: %s", f"{agent.total_prompt_tokens:,}")
        agent.logger.info("  • Total completion tokens: %s", f"{agent.total_completion_tokens:,}")
        agent.logger.info("  • Total tokens used: %s", f"{agent.total_tokens_used:,}")
        if agent.total_cached_tokens > 0:
            cache_percentage = (agent.total_cached_tokens * 100) // agent.total_prompt_tokens if agent.total_prompt_tokens > 0 else 0
            agent.logger.info(
                "  • Total cached tokens: %s (%s%% of prompts)",
                f"{agent.total_cached_tokens:,}",
                cache_percentage,
            )
            agent.logger.info("  • Cache savings: ~%s tokens", f"{agent.total_cached_tokens:,}")
        agent.logger.info(
            "  • Average tokens per step: %s",
            f"{agent.total_tokens_used // (iteration + 1):,}",
        )
        agent.logger.info("%s%s%s", Colors.GREEN, "=" * 50, Colors.RESET)
