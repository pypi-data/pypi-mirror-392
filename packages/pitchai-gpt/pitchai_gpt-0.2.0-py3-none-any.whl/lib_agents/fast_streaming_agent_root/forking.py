"""
Forked response generation utilities for FastStreamingAgent.

Provides helpers to duplicate the current conversation, append extra
instructions (system/user prompts), and request an additional completion from
the LLM without mutating the primary message history.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..gpt.gpt import GPT
from .ui_helpers import UILiveStreamer


class ForkingError(RuntimeError):
    """Raised when a configured fork cannot be executed."""


@dataclass
class ForkExecutionResult:
    """Represents the outcome of a forked generation."""

    generated_text: str
    append_to_last_assistant: bool = False
    newline_prefix: str = "\n\n"
    stream_target: Optional[str] = None
    streamed: bool = False


class ForkedResponder:
    """Generate forked responses based on configuration."""

    def __init__(self, agent_instance: Any) -> None:
        self.agent = agent_instance

    async def generate(
        self,
        trigger: str,
        *,
        base_text: Optional[str] = None,
        stream_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Optional[ForkExecutionResult]:
        """
        Generate a forked response for the given trigger.

        Parameters
        ----------
        trigger:
            Name of the configured fork (e.g. "final_answer", "suggestions").
        base_text:
            Optional text from the main run (e.g. raw final answer) that can be
            interpolated into fork prompts.

        Returns
        -------
        Optional[ForkExecutionResult]
            A result when the fork is configured and executed, otherwise ``None``.

        Raises
        ------
        ForkingError
            If the fork is enabled but misconfigured or the LLM returns an empty payload.
        """
        fork_config = getattr(self.agent.config, "forked_responses", None)
        if not fork_config:
            return None

        fork_definition = fork_config.get(trigger)
        if not fork_definition or not fork_definition.enabled:
            return None

        # Build a pristine copy of the conversation (role/content only)
        messages_copy: List[Dict[str, str]] = []
        for message in self.agent.messages:
            role = message.get("role")
            content = message.get("content")
            if role == "tool":
                messages_copy.append({"role": "user", "content": str(content or "")})
                continue

            if isinstance(role, str):
                entry: Dict[str, str] = {"role": role}
                if isinstance(content, str):
                    entry["content"] = content
                messages_copy.append(entry)

        if not messages_copy:
            raise ForkingError("Conversation is empty; cannot fork response.")

        replacements = self._build_replacements(base_text)

        system_prompt = fork_definition.system_prompt.format(**replacements) if fork_definition.system_prompt else ""
        user_prompt = fork_definition.user_prompt.format(**replacements) if fork_definition.user_prompt else ""

        fork_messages = copy.deepcopy(messages_copy)
        if system_prompt.strip():
            fork_messages.append({"role": "system", "content": system_prompt.strip()})
        if user_prompt.strip():
            fork_messages.append({"role": "user", "content": user_prompt.strip()})

        if len(fork_messages) == len(messages_copy):
            raise ForkingError(
                f"Fork '{trigger}' enabled but provided no additional prompts."
            )

        model_name = fork_definition.model
        if not model_name:
            if trigger == "suggestions":
                model_name = getattr(self.agent.config, "suggestions_model", None)
            else:
                model_name = getattr(self.agent, "model", None)
        if not model_name:
            raise ForkingError(f"Fork '{trigger}' is enabled but no model is configured.")

        enable_streaming = False
        streamer: Optional[UILiveStreamer] = None
        if stream_kwargs and fork_definition.stream_target:
            stream_target = fork_definition.stream_target
            if stream_target == stream_kwargs.get("stream_target", stream_target):
                shared_ui_msg = stream_kwargs.get("shared_ui_msg")
                if shared_ui_msg:
                    streamer = UILiveStreamer(
                        shared_ui_msg=shared_ui_msg,
                        speed=stream_kwargs.get("speed", 0.001),
                        use_grpc=stream_kwargs.get("use_grpc", False),
                        overwrite=stream_kwargs.get("overwrite", True),
                    )
                    enable_streaming = True

        gpt = GPT(model=model_name, msg_list=fork_messages)

        generated_text = ""
        streamed = False

        observers = []
        create_observer = getattr(self.agent, "_create_dataset_usage_observer", None)
        if callable(create_observer):
            dataset_observer = create_observer()
            if dataset_observer:
                observers.append(dataset_observer)

        try:
            if enable_streaming and streamer:
                response_stream = await gpt.get_text_response(
                    msg_list=fork_messages,
                    silent=True,
                    return_raw_stream=True,
                    stream_observers=observers or None,
                )
                parts: List[str] = []
                async for chunk in response_stream:
                    if not getattr(chunk, "choices", None):
                        continue
                    if len(chunk.choices) == 0:
                        continue
                    delta = chunk.choices[0].delta.content
                    if not delta:
                        continue
                    parts.append(delta)
                    await streamer.enqueue(delta)
                await streamer.finish()
                streamed = True
                generated_text = "".join(parts)
            else:
                response_text = await gpt.get_text_response(
                    msg_list=fork_messages,
                    silent=True,
                    return_raw_stream=False,
                    stream_observers=observers or None,
                )
                generated_text = response_text
        finally:
            if streamer and streamer.active:
                await streamer.finish()

        generated = generated_text.strip()
        if not generated:
            raise ForkingError(f"Fork '{trigger}' produced an empty response.")

        return ForkExecutionResult(
            generated_text=generated,
            append_to_last_assistant=fork_definition.append_to_last_assistant,
            newline_prefix=fork_definition.newline_prefix,
            stream_target=fork_definition.stream_target,
            streamed=streamed,
        )

    def _build_replacements(self, base_text: Optional[str]) -> Dict[str, str]:
        """Prepare common placeholder replacements for fork prompts."""
        last_assistant = ""
        if self.agent.messages:
            for message in reversed(self.agent.messages):
                if message.get("role") == "assistant":
                    last_assistant = str(message.get("content", ""))
                    break

        replacements = {
            "raw_text": base_text or "",
            "base_text": base_text or "",
            "final_answer": base_text or "",
            "last_assistant": last_assistant,
            "user_query": getattr(self.agent, "original_user_query", ""),
        }
        return replacements
