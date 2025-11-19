"""UI helper functions for FastStreamingAgent.

This module contains UI-related functions that handle templating,
rendering, and streaming to the UI.
"""

import asyncio
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator

from jinja2 import Environment, FileSystemLoader

if TYPE_CHECKING:
    from .step_state import StepContainerState

from .embed_utils import replace_embed_tags

LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[5]
TEMPLATE_DIR = PROJECT_ROOT / "apps" / "web_app" / "src" / "web_app" / "web" / "templates"
JINJA_ENV = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


async def push_action_to_panel(
    agent: Any,
    dutch_description: str,
    shared_ui_msg: Any,
    agent_id: str,
    conversation_id: str | None
) -> None:
    """Push an action description to the action panel (ui2).

    Args:
        agent: The agent instance (for logging)
        dutch_description: The Dutch step description with emoji prefix
        shared_ui_msg: The shared UI message object
        agent_id: The agent ID for streaming
        conversation_id: The conversation ID
    """
    if not shared_ui_msg:
        return

    parts = dutch_description.split(" ", 1)
    if len(parts) == 2 and any(ord(c) > 127 for c in parts[0]):
        emoji = parts[0]
        text = parts[1]
    else:
        emoji = "📊"
        text = dutch_description

    action_template = JINJA_ENV.get_template("components/action_item.html")
    action_html = action_template.render(emoji=emoji, text=text)

    existing_actions = getattr(shared_ui_msg, "ui2", "")
    if not existing_actions:
        header_template = JINJA_ENV.get_template("components/action_panel_header.html")
        existing_actions = header_template.render()

    updated_actions = existing_actions + "\n" + action_html

    await shared_ui_msg.set_content_instantly(
        content=updated_actions,
        property="ui2",
        overwrite=True,
        to_main_process=True,
        pipeline_id=conversation_id,
        requester_id=agent_id
    )


def _word_chunks(text: str) -> Iterator[str]:
    """Yield text chunks word-by-word while preserving whitespace."""
    if not text:
        return

    position = 0
    for match in re.finditer(r"\S+\s*", text):
        start, end = match.span()
        if start > position:
            yield text[position:start]
        yield match.group(0)
        position = end

    if position < len(text):
        remainder = text[position:]
        if remainder:
            yield remainder


async def stream_final_answer(
    agent: Any,
    shared_ui_msg: Any,
    final_text: str,
    *,
    overwrite: bool = True,
    use_grpc: bool | None = None,
) -> None:
    """Stream the final answer word-by-word to the UI."""
    if not final_text or not shared_ui_msg:
        return

    speed = 0.001
    config = getattr(agent, "config", None)
    if config and getattr(config, "ui_streaming", None):
        speed = getattr(config.ui_streaming, "final_answer_speed", speed)

    stream_kwargs = {
        "chunk_stream": _word_chunks(final_text),
        "property": "content",
        "overwrite": overwrite,
        "speed": speed,
        "silent": True,
        "skip_grpc": True,
    }

    if use_grpc is None:
        use_grpc = hasattr(shared_ui_msg, "acquire_streaming_lock")

    if use_grpc:
        stream_kwargs["skip_grpc"] = False

    await shared_ui_msg.stream_into(**stream_kwargs)


class UILiveStreamer:
    """Asynchronously stream chunks into the shared UI message as they arrive."""

    def __init__(
        self,
        shared_ui_msg: Any,
        *,
        speed: float,
        use_grpc: bool,
        overwrite: bool,
        style_class: str | None = None,
    ) -> None:
        self.shared_ui_msg = shared_ui_msg
        self.speed = speed
        self.use_grpc = use_grpc
        self.overwrite = overwrite
        self.style_class = style_class
        self._queue: asyncio.Queue[str | object] = asyncio.Queue()
        self._sentinel = object()
        self.active: bool = True
        self._task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        async def generator():
            while True:
                chunk = await self._queue.get()
                if chunk is self._sentinel:
                    break
                if chunk:
                    yield chunk

        try:
            await self.shared_ui_msg.stream_into(
                generator(),
                property="content",
                overwrite=self.overwrite,
                speed=self.speed,
                silent=True,
                skip_grpc=not self.use_grpc,
                style_class=self.style_class,
            )
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.debug("UILiveStreamer aborted: %s", exc)
        finally:
            self.active = False

    async def enqueue(self, chunk: str) -> None:
        if not self.active or not chunk:
            return
        await self._queue.put(chunk)

    async def finish(self) -> None:
        if not self.active:
            return
        await self._queue.put(self._sentinel)
        await self._task

    async def cancel(self) -> None:
        if not self.active:
            return
        await self._queue.put(self._sentinel)
        try:
            await asyncio.wait_for(self._task, timeout=1)
        except asyncio.TimeoutError:
            self._task.cancel()
        finally:
            self.active = False


async def flush_final_answer(
    agent: Any,
    final_answer_accumulator: list[str],
    execution_globals: dict[str, Any],
    shared_ui_msg: Any,
    final_answer_id: str,
    conversation_id: str | None
) -> None:
    """Flush the accumulated final answer to UI in one go.

    Args:
        agent: The agent instance (for logging)
        final_answer_accumulator: List of answer chunks to combine
        execution_globals: Execution globals for embed tag processing
        shared_ui_msg: The shared UI message object
        final_answer_id: The final answer ID for streaming
        conversation_id: The conversation ID
    """
    if not final_answer_accumulator or not shared_ui_msg:
        return

    full_answer = "".join(final_answer_accumulator)

    enable_client_embeds = True
    config = getattr(agent, "config", None)
    ui_stream_cfg = getattr(config, "ui_streaming", None) if config else None
    if ui_stream_cfg and hasattr(ui_stream_cfg, "enable_embeds"):
        enable_client_embeds = getattr(ui_stream_cfg, "enable_embeds")
    elif hasattr(shared_ui_msg, "enable_embeds"):
        enable_client_embeds = bool(shared_ui_msg.enable_embeds)

    if not enable_client_embeds:
        try:
            full_answer = replace_embed_tags(agent, full_answer)
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.debug("Failed to process embed tags: %s", exc)

    LOGGER.debug("Flushing final answer with %s chars", len(full_answer))

    if execution_globals:
        variables = list(execution_globals.keys())[:30]
        LOGGER.debug("Variables available in execution_globals for final answer: %s", variables)

    LOGGER.debug("Sending final answer to UI with requester_id=%s", final_answer_id)
    if isinstance(final_answer_accumulator, list):
        final_answer_accumulator.clear()
        final_answer_accumulator.append(full_answer)
    set_kwargs = {
        "content": full_answer,
        "property": "content",
        "overwrite": False,
        "requester_id": final_answer_id,
        "skip_grpc": True,
    }

    if hasattr(shared_ui_msg, "acquire_streaming_lock"):
        set_kwargs["to_main_process"] = True
        set_kwargs.pop("skip_grpc", None)

    await shared_ui_msg.set_content_instantly(**set_kwargs)
    LOGGER.debug("Final answer sent successfully")


def acquire_final_answer_lock(
    agent: Any,
    shared_ui_msg: Any,
    final_answer_id: str
) -> bool:
    """Acquire exclusive streaming rights for final answer.

    Args:
        agent: The agent instance (for logging)
        shared_ui_msg: The shared UI message object
        final_answer_id: The final answer ID for streaming

    Returns:
        True if lock was acquired successfully, False otherwise
    """
    if not shared_ui_msg:
        return False

    if not hasattr(shared_ui_msg, "acquire_streaming_lock"):
        LOGGER.debug("Streaming lock unsupported; proceeding without acquiring lock")
        return True

    success = shared_ui_msg.acquire_streaming_lock(final_answer_id)
    if success:
        LOGGER.debug("Final answer streaming lock acquired by %s", final_answer_id)
        return True

    LOGGER.warning(
        "Could not acquire streaming lock - held by %s",
        shared_ui_msg.streaming_lock,
    )
    return False


async def update_step_ui(
    agent: Any,
    state: "StepContainerState"
) -> None:
    """Update step UI badge to executing status.

    Args:
        agent: The agent instance
        state: The step container state
    """
    if (agent.config.dutch_step_descriptions.enabled and
        hasattr(agent, "shared_ui_msg") and agent.shared_ui_msg and
        state.step_ids_set and
        not (hasattr(agent, "waiting_for_final_answer") and agent.waiting_for_final_answer)):

        await agent.shared_ui_msg.broadcast_update_badge(
            element_id=f"content-{state.badge_id}",
            status="executing",
            html='<i class="fa-solid fa-cog fa-spin mr-1.5"></i> Uitvoeren'
        )


async def stream_step_to_ui(
    agent: Any,
    step_number: int,
    state: "StepContainerState",
    content: str,
    was_in_code_block: bool
) -> None:
    """Stream step reasoning content to UI.

    Args:
        agent: The agent instance
        step_number: Current step number
        state: The step container state
        content: Content to stream
        was_in_code_block: Whether we were in a code block before this content
    """
    if (agent.config.dutch_step_descriptions.enabled and
        hasattr(agent, "shared_ui_msg") and agent.shared_ui_msg and
        not was_in_code_block and
        not state.in_code_block and
        state.processed_blocks == 0 and
        not (hasattr(agent, "waiting_for_final_answer") and agent.waiting_for_final_answer)):

        if not state.step_ids_set and content.strip():
            state.step_id = f"step-{step_number}"
            state.title_dutch_id = f"{state.step_id}-dutch"
            state.badge_id = f"{state.step_id}-badge"
            state.reasoning_id = f"{state.step_id}-reasoning"
            state.code_id = f"{state.step_id}-code"
            state.output_id = f"{state.step_id}-output"
            state.reasoning_container_id = f"content-{state.step_id}-reasoning-container"
            state.code_container_id = f"content-{state.step_id}-code-container"
            state.output_container_id = f"content-{state.step_id}-output-container"
            state.step_ids_set = True

            loading_emoji = "⏳"
            template = JINJA_ENV.get_template("components/agent_step_container.html")
            template_html = template.render(
                state=state,
                loading_emoji=loading_emoji
            )
            await agent.shared_ui_msg.set_content_instantly(
                template_html,
                property="content",
                overwrite=False,
                to_main_process=True,
                pipeline_id=getattr(agent, "conversation_id", None),
                requester_id=agent.agent_id
            )
            state.step_container_sent = True

        state.step_reasoning_buffer += content

        if state.step_ids_set and not state.step_reasoning_shown and state.step_reasoning_buffer.strip():
            state.step_reasoning_shown = True
            await agent.shared_ui_msg.broadcast_show_element(state.reasoning_container_id)

        if state.step_ids_set and content.strip():
            await agent.shared_ui_msg.stream_into(
                content,
                property="content",
                stream_insert_id=state.reasoning_id,
                speed=0.001,
                skip_grpc=True,
                requester_id=agent.agent_id
            )
