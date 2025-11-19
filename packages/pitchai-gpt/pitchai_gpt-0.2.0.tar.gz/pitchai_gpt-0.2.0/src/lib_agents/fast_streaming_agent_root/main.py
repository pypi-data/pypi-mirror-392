#!/usr/bin/env python3
# Copyright (c) 2024 FastStreamingAgent Contributors
"""Fast Streaming Agent - Execute code blocks immediately as they complete in the token stream.

This agent streams GPT responses, detects complete code blocks in real-time,
executes them immediately, and injects the output back into the conversation.
"""

import argparse
import asyncio
import html
import json
import logging
import os
import re
import sys
import uuid
from collections.abc import Awaitable
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict
import inspect

import pandas as pd

from dotenv import load_dotenv

from .text_utils import strip_code_fence
from .table_registry import TableRegistry
from . import pandas_type_guard  # noqa: F401 - applies pandas dtype warnings

PROJECT_ROOT = Path(__file__).resolve().parents[5]
LIB_AGENTS_SRC = PROJECT_ROOT / "libs" / "lib_agents" / "src"
LIB_UTILS_SRC = PROJECT_ROOT / "libs" / "lib_utils" / "src"
LIB_DB_SRC = PROJECT_ROOT / "libs" / "lib_db" / "src"
LIB_SEARCH_SRC = PROJECT_ROOT / "libs" / "lib_search" / "src"
WEB_APP_SRC = PROJECT_ROOT / "apps" / "web_app" / "src"

for path in (LIB_AGENTS_SRC, LIB_UTILS_SRC, LIB_DB_SRC, LIB_SEARCH_SRC, WEB_APP_SRC):
    if str(path) not in sys.path:
        sys.path.append(str(path))

from libs.lib_utils.src.lib_utils.code_ops.aexec import (
    DEFAULT_ADDITIONAL_BUILTINS,
    DEFAULT_ALLOWED_IMPORTS,
    RestrictedExecutionRuntime,
    async_execute_catch_logs_errors,
)

from .dataframe_loader import load_configured_dataframes
from .agent_config import AgentConfig
from .config_resolver import resolve_agent_config_path_sync
from .ui_helpers import (
    push_action_to_panel,
    flush_final_answer,
    acquire_final_answer_lock,
    update_step_ui,
    stream_step_to_ui,
    stream_final_answer,
    UILiveStreamer,
)
from .stop_helpers import should_stop, stop_or_next_phase
from .token_helpers import update_total_token_usage, print_step_tokens_used, print_token_summary
from .dutch_step_ui import generate_and_display_dutch_step_ui

# search_company_knowledge is now loaded from config
from .suggestions import generate_and_stream_suggestions
from ..gpt.gpt import GPT
from .code_block_utils import (
    apply_colors,
    detect_complete_code_blocks,
)
from .code_storage import save_code_block
from .colors import Colors
from .semantic_layer_runtime import (
    ensure_semantic_layer_index,
    load_semantic_layer_dataframes,
)
from .preloaded_state import cache_preloaded_state, has_preloaded_state
from .state_serialization import (
    deserialize_agent,
    load_agent_state_from_wasabi,
    save_agent_state,
    save_agent_state_to_wasabi,
)
from .stream_inspector import DatasetInfo
from .dataset_usage import build_dataset_alias_map, create_dataset_usage_observer
from .search_usage import install_search_wrappers

# Functions are now loaded from config - see _load_configured_functions()
from .custom_print import PrintCapture
from .error_collapse import collapse_error_sequences
from .function_loader import load_configured_functions
from .function_wrapper import wrap_configured_functions
from .pre_action_loader import PreActionLoader
from .second_step_primer import SecondStepPrimer
from .step_describer import describe_step_in_dutch
from .token_guard import TokenLengthGuard
from .verification_step_loader import VerificationStepLoader
from .code_apply import code_apply
from .step_state import StepContainerState, StepLog, CodeBlockLog
from .forking import ForkedResponder

if TYPE_CHECKING:
    pass

LOGGER = logging.getLogger(__name__)


class RequestContext(Enum):
    """Enum for tracking the current request context."""

    INITIAL = "initial"
    DETAIL = "detail"
    FINAL_ANSWER = "final_answer"
    FOLLOW_UP = "follow_up"


class FastStreamingAgent:
    """Fast streaming agent for real-time code execution."""

    def __init__(
        self,
        model: str | None = None,
        *,
        testing: bool = False,
        max_output_tokens: int | None = None,
        agent_config: str | None = None,
        load_state_dataframes: bool = True,
        depth: int = 0,
        disable_error_collapse: bool = False,
        enable_suggestions: bool = True,
    ) -> None:
        """Initialize the fast streaming agent.

        Args:
            model: Model to use for generation.
            disable_error_collapse: If True, disables collapsing of error sequences.
            testing: Whether in testing mode.
            max_output_tokens: Maximum tokens allowed in code execution output.
            agent_config: Path to agent configuration JSON file.
            load_state_dataframes: Whether to load dataframes from instant state.
            depth: Current recursion depth for sub-agents.
            enable_suggestions: Whether to generate suggestions after final answer.
        """
        self.logger = LOGGER
        self.execution_functions: dict[str, object] = {}
        self.testing: bool = testing
        self.depth: int = depth
        self.load_state_dataframes = load_state_dataframes
        self.agent_todos: str = ""  # Agent's own todo list
        self.file_attachments: dict[str, dict] = {}  # File attachments with extracted text
        self.shared_ui_msg: Any | None = None
        self.project_root = PROJECT_ROOT
        self.agent_config_path = str(Path(agent_config).resolve()) if agent_config else None
        preloaded_available = has_preloaded_state(self.agent_config_path) if self.agent_config_path else False
        import os

        self.logger.info(
            "Preloaded state available for %s: %s [pid=%s]",
            self.agent_config_path or "<unknown>",
            preloaded_available,
            os.getpid(),
        )

        self.semantic_layer_registry: dict[str, Any] = {}
        self.semantic_layer_failures: list[dict[str, Any]] = []
        self._semantic_layer_indexed: bool = False

        # Load agent configuration
        if agent_config:
            self.config = AgentConfig.from_file(agent_config)
            self.logger.info("Loaded agent configuration from %s", agent_config)
        else:
            self.config = AgentConfig.create_default()

        execution_cfg = getattr(self.config, "execution", None)
        self.execution_mode: str = getattr(execution_cfg, "mode", "code_blocks")
        tool_function_cfg = getattr(execution_cfg, "tool_function", None)
        default_tool_name = getattr(tool_function_cfg, "name", "execute_python")
        self.tool_function_name: str = default_tool_name
        self.tool_mode_enabled: bool = self.execution_mode == "tool_calls"
        self.tool_specs: list[dict[str, Any]] | None = None
        self.tool_choice: dict[str, Any] | None = None
        if self.tool_mode_enabled and execution_cfg is not None:
            spec = execution_cfg.build_tool_spec()
            self.tool_specs = [spec]
            function_name = spec.get("function", {}).get("name") or default_tool_name
            self.tool_function_name = function_name
            self.tool_choice = {"type": "function", "function": {"name": function_name}}

        # Apply model from config or parameter (parameter overrides config)
        self.model: str = model if model is not None else self.config.model

        # Apply configuration values (with parameter overrides)
        self.max_depth: int = self.config.limits.max_subagent_depth
        self.max_output_tokens: int = max_output_tokens if max_output_tokens is not None else self.config.limits.max_output_tokens
        self.disable_error_collapse: bool = disable_error_collapse or not self.config.error_collapse.enabled
        self.enable_suggestions: bool = self.config.enable_suggestions if enable_suggestions else False

        # Stream Dutch step reasoning only when explicitly enabled to avoid noisy WS errors
        self.stream_steps_to_ui: bool = os.getenv("FAST_AGENT_STREAM_STEPS", "false").lower() in {"1", "true", "yes"}

        # Generate unique agent ID for streaming lock system
        self.agent_id: str = f"agent_{uuid.uuid4().hex[:8]}"
        # Separate ID for final answer to ensure exclusivity
        self.final_answer_id: str = f"final_{uuid.uuid4().hex[:8]}"

        # Load configured functions into execution globals
        load_configured_functions(self.config, self.execution_functions, agent=self)

        # Create print capture for THIS agent (each agent has its own)
        print_capture = PrintCapture()

        # Register code_apply function first
        self.execution_functions["code_apply"] = code_apply

        # Wrap all configured functions with generic output formatting
        wrap_configured_functions(
            execution_globals=self.execution_functions,
            function_configs=self.config.functions.available_functions,
            print_capture=print_capture,
            special_functions=["stop", "task", "todo_write", "code_apply"],
        )

        # Register special functions (always available)
        self.execution_functions["stop"] = self._handle_stop
        self.execution_functions["task"] = self._create_subtask_agent
        self.execution_functions["todo_write"] = self._handle_todo_write
        self.execution_functions["print"] = print_capture.custom_print

        install_search_wrappers(self)

        (
            runtime_allowed_imports,
            runtime_additional_builtins,
            runtime_write_guard,
            runtime_enable_restrictions,
        ) = self.config.runtime_security.build_runtime_options(
            DEFAULT_ALLOWED_IMPORTS,
            DEFAULT_ADDITIONAL_BUILTINS,
        )

        # Restricted runtime that exposes only the curated function surface
        self.execution_runtime = RestrictedExecutionRuntime(
            system_bindings=self.execution_functions,
            user_state={},
            allowed_imports=runtime_allowed_imports,
            additional_builtins=runtime_additional_builtins,
            write_guard=runtime_write_guard,
            enable_restrictions=runtime_enable_restrictions,
        )
        self.execution_runtime.refresh_protected_names()
        self.execution_globals = self.execution_runtime.user_state
        self.loaded_dataframes = load_configured_dataframes(self, PROJECT_ROOT)
        self.semantic_layer_registry = load_semantic_layer_dataframes(self, PROJECT_ROOT)
        self._dataset_events_emitted: set[str] = set()
        self._dataset_alias_map: Dict[str, DatasetInfo] = build_dataset_alias_map(self)
        try:
            if (
                self.agent_config_path
                and not has_preloaded_state(self.agent_config_path)
            ):
                base_frames = getattr(self, "_base_dataframe_sources", {})
                if base_frames or self.semantic_layer_registry:
                    cache_preloaded_state(
                        config_path=self.agent_config_path,
                        dataframe_format=self.config.get_dataframe_load_settings().format,
                        base_frames=base_frames,
                        semantic_registry=self.semantic_layer_registry,
                    )
                    self.logger.info(
                        "Cached base and semantic dataframes for %s",
                        self.agent_config_path,
                    )
        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.debug(
                "Unable to cache preloaded state for %s: %s",
                self.agent_config_path,
                exc,
            )
        self.table_registry = TableRegistry()

        # Stop control flags
        self.stop_requested: bool = False
        self.stop_summary: str = ""
        self.final_answer_produced: bool = False

        # Initialize token guard
        self.token_guard = TokenLengthGuard(max_tokens=self.max_output_tokens, model=self.model)

        # Initialize pre-action loader with config dict
        self.pre_action_loader = PreActionLoader(config_dict=self.config.model_dump())

        # Initialize second step primer (uses same config dict)
        self.second_step_primer = SecondStepPrimer(config_dict=self.config.model_dump())

        # Initialize verification step loader (uses same config dict)
        self.verification_step_loader = VerificationStepLoader(config_dict=self.config.model_dump())

        # Forked response manager
        self.fork_manager = ForkedResponder(self)

        # Initialize logging
        self.session_log: dict[str, object] = {
            "session_id": datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now(tz=timezone.utc).isoformat(),
            "model": model,
            "steps": [],
        }

        # Initialize token tracking
        self.total_tokens_used = 0
        self.total_cached_tokens = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

        # Store conversation messages on the instance
        self.messages: list[dict[str, str]] = []

        self.active_streaming_tasks: list[asyncio.Task[Any]] = []
        self._background_tasks: list[asyncio.Task[Any]] = []

        # Flag to indicate if this is a follow-up message
        self.is_follow_up: bool = False

        # Track request context for stop signal handling
        self.request_context: RequestContext = RequestContext.INITIAL

    def _create_subtask_agent(self, *args, **kwargs):
        """Placeholder for environments without sub-agent support."""

        self.logger.warning("Subtask agent creation not available in CLI mode")
        return "Subtask agent creation is disabled in this environment."

    def _print_indented(self, content: str, *, end: str = "\n", flush: bool = False) -> None:
        """Simplified pretty printer compatible with CLI usage."""

        print(content, end=end, flush=flush)

    def _cancel_active_streaming_tasks(self) -> None:
        """Cancel all active streaming tasks to prevent interference with final answer."""
        for task in list(self.active_streaming_tasks):
            if not task.done():
                task.cancel()
            self.active_streaming_tasks.remove(task)

    def _schedule_task(self, awaitable: Awaitable[Any], *, track: bool = False) -> asyncio.Task[Any]:
        """Create and track a background task."""

        task = asyncio.create_task(awaitable)
        target_list = self.active_streaming_tasks if track else self._background_tasks
        target_list.append(task)

        def _cleanup(completed: asyncio.Task[Any]) -> None:
            if completed in target_list:
                target_list.remove(completed)

        task.add_done_callback(_cleanup)
        return task

    async def _push_action_to_panel(self, dutch_description: str) -> None:
        """Push an action description to the action panel (ui2)."""
        await push_action_to_panel(
            agent=self,
            dutch_description=dutch_description,
            shared_ui_msg=getattr(self, "shared_ui_msg", None),
            agent_id=self.agent_id,
            conversation_id=getattr(self, "conversation_id", None),
        )

    @classmethod
    async def load_agent_state(
        cls,
        conversation_id: str,
        chatconfig_id: str | None = None,
    ) -> "FastStreamingAgent | None":
        """Load a serialized agent state from remote storage, falling back to disk."""

        agent = await load_agent_state_from_wasabi(conversation_id, chatconfig_id)
        if agent:
            LOGGER.info("%sLoaded serialized agent for %s from Wasabi%s", Colors.GREEN, conversation_id, Colors.RESET)
            return agent

        agent_file = Path("data/agents") / f"{conversation_id}.dill"
        if not agent_file.exists():
            return None

        try:
            payload = agent_file.read_bytes()
            agent = deserialize_agent(payload)
            setattr(agent, "conversation_id", conversation_id)
            setattr(agent, "chatconfig_id", chatconfig_id)

            file_size = agent_file.stat().st_size / 1024  # KB
            LOGGER.info(
                "%sLoaded serialized agent from %s (%.1f KB)%s",
                Colors.GREEN,
                agent_file,
                file_size,
                Colors.RESET,
            )
            return agent
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("%sError loading serialized agent from disk: %s%s", Colors.RED, exc, Colors.RESET)
            return None

    async def _flush_final_answer(self) -> None:
        """Flush the accumulated final answer to UI in one go."""
        if hasattr(self, "final_answer_accumulator") and self.final_answer_accumulator:
            await flush_final_answer(
                agent=self,
                final_answer_accumulator=self.final_answer_accumulator,
                execution_globals=self.execution_globals if hasattr(self, "execution_globals") else {},
                shared_ui_msg=getattr(self, "shared_ui_msg", None),
                final_answer_id=self.final_answer_id,
                conversation_id=getattr(self, "conversation_id", None),
            )
            # Clear accumulator
            self.final_answer_accumulator = []

    def _acquire_final_answer_lock(self) -> bool:
        """Acquire exclusive streaming rights for final answer."""
        return acquire_final_answer_lock(
            agent=self, shared_ui_msg=getattr(self, "shared_ui_msg", None), final_answer_id=self.final_answer_id
        )

    def _inject_final_answer_instruction(self) -> None:
        """Append final-answer instructions from config exactly once."""
        if getattr(self, "_final_instruction_injected", False):
            return

        instruction = getattr(self.config.multi_step, "final_answer_message", None)
        if not instruction:
            return

        self.messages.append({
            "role": "system",
            "content": instruction,
        })
        self._final_instruction_injected = True
        self.logger.info("%s[Final answer instruction injected]%s", Colors.YELLOW, Colors.RESET)

    async def _maybe_stream_final_answer(self, assistant_response: str, *, had_error: bool, has_code_output: bool) -> None:
        """Stream text-only final answers to the UI and cache for persistence."""
        if had_error or has_code_output:
            return

        cleaned = strip_code_fence(assistant_response).strip()

        # Extract the text within <final_answer> tags if present
        final_answer_match = re.search(r"<final_answer>(.*?)</final_answer>", cleaned, re.DOTALL)
        if final_answer_match:
            cleaned = final_answer_match.group(1).strip()

        fork_result = None
        stream_kwargs = None
        shared_ui_msg = getattr(self, "shared_ui_msg", None)
        supports_stream_lock = hasattr(shared_ui_msg, "acquire_streaming_lock") if shared_ui_msg else False
        lock_acquired = False
        if shared_ui_msg:
            speed = getattr(getattr(self.config, "ui_streaming", None), "final_answer_speed", 0.001)
            if supports_stream_lock:
                lock_acquired = self._acquire_final_answer_lock()
                if lock_acquired:
                    self.final_answer_lock_acquired = True
            stream_kwargs = {
                "shared_ui_msg": shared_ui_msg,
                "speed": speed,
                "use_grpc": lock_acquired if supports_stream_lock else False,
                "overwrite": True,
                "stream_target": "final_answer",
            }

        fork_result = None
        if hasattr(self, "fork_manager"):
            fork_result = await self.fork_manager.generate(
                "final_answer",
                base_text=cleaned,
                stream_kwargs=stream_kwargs,
            )

        final_text = cleaned
        if fork_result and fork_result.generated_text:
            final_text = fork_result.generated_text

        append_to_last = True
        newline_prefix = "\n\n"
        if fork_result:
            append_to_last = fork_result.append_to_last_assistant
            newline_prefix = fork_result.newline_prefix or "\n\n"

        if append_to_last and self.messages:
            last_message = self.messages[-1]
            if isinstance(last_message, dict) and last_message.get("role") == "assistant":
                last_content = str(last_message.get("content", ""))
                last_message["content"] = f"{last_content}{newline_prefix}{final_text}"

        # Ensure the accumulated final answer reflects the forked response
        self.final_answer_accumulator = [final_text]

        if shared_ui_msg:
            final_streamed = bool(fork_result and fork_result.streamed)

            if final_streamed:
                pass
            else:
                if getattr(self, "_live_streamer_used", False):
                    set_kwargs = {
                        "content": final_text,
                        "property": "content",
                        "overwrite": True,
                    }
                    if supports_stream_lock and lock_acquired:
                        set_kwargs["to_main_process"] = True
                    else:
                        set_kwargs["skip_grpc"] = True
                    await shared_ui_msg.set_content_instantly(**set_kwargs)
                else:
                    await stream_final_answer(
                        agent=self,
                        shared_ui_msg=shared_ui_msg,
                        final_text=final_text,
                        overwrite=True,
                        use_grpc=lock_acquired if supports_stream_lock else None,
                    )
        if hasattr(self, "_live_streamer_used"):
            delattr(self, "_live_streamer_used")

        self.final_answer_produced = True

    def _handle_stop(self, summary: str = "Task completed") -> str:
        """Handle stop function call.

        Args:
            summary: Summary message for stop reason.

        Returns:
            Stop confirmation message.
        """
        self.stop_requested = True
        self.stop_summary = summary
        stop_message = f"🛑 STOPPING: {summary}"
        self._print_indented(stop_message)  # Print to stdout so it appears in logs
        return stop_message

    def _handle_todo_write(self, todos: str) -> str:
        """Handle todo list management for the agent.

        Args:
            todos: Markdown-formatted todo list string (e.g., "- [ ] Task 1\n- [x] Task 2").

        Returns:
            Formatted todo list display.
        """
        # Store the todo list

        return "✅ TODO list updated."

    def register_table(self, variable_name: str, table: Any) -> None:
        """Register a DataFrame for later retrieval by the UI."""
        self.table_registry.register(variable_name, table)

    def get_registered_table(self, variable_name: str) -> pd.DataFrame | None:
        """Return a previously registered DataFrame if available."""
        return self.table_registry.get(variable_name)

    def resolve_table(self, variable_name: str) -> pd.DataFrame | None:
        """Locate a DataFrame by name from registered tables or execution globals."""
        lookup = None
        if hasattr(self, "execution_globals") and isinstance(self.execution_globals, dict):
            lookup = self.execution_globals.get
        return self.table_registry.resolve(variable_name, lookup)

    async def _status_update(self, message: str | None) -> None:
        """Send a status update to the UI if the status function is available."""
        if not message:
            return

        status_callable = None
        if hasattr(self, "execution_globals") and isinstance(self.execution_globals, dict):
            status_callable = self.execution_globals.get("status")
        if not status_callable:
            return

        shared_ui_msg = getattr(self, "shared_ui_msg", None)
        if not shared_ui_msg:
            return

        conversation_id = getattr(self, "conversation_id", None)
        try:
            result = status_callable(message, shared_ui_msg=shared_ui_msg, conversation_id=conversation_id)
            if inspect.isawaitable(result):
                await result
        except Exception as exc:
            self.logger.debug("Status update failed: %s", exc)

    def reset_analysis_flags(self) -> None:
        """Reset analysis state flags to allow full analysis cycle on follow-up messages.

        This method should be called before processing follow-up messages to ensure
        the agent goes through the complete analysis process (detail → final answer).
        """
        # Remove all analysis state flags if they exist

        if hasattr(self, "verification_done"):
            delattr(self, "verification_done")
        if hasattr(self, "final_answer_accumulator"):
            delattr(self, "final_answer_accumulator")
        if hasattr(self, "final_answer_lock_acquired"):
            delattr(self, "final_answer_lock_acquired")
        if hasattr(self, "_final_instruction_injected"):
            delattr(self, "_final_instruction_injected")

        # Reset stop flags
        self.stop_requested = False
        self.stop_summary = ""

        self.logger.info("%s[Analysis Flags Reset]%s", Colors.BLUE, Colors.RESET)
        self.logger.info("%sReady for new analysis cycle...%s", Colors.BLUE, Colors.RESET)

    async def execute_pre_actions(self, messages: list[dict[str, str]], user_query: str) -> str:
        """Execute pre-configured actions before the main conversation.

        Args:
            messages: Conversation messages list to append to.
            user_query: The user's query for template replacement.

        Returns:
            Combined output from all pre-actions.
        """
        if not self.pre_action_loader.is_enabled():
            return ""

        # Get formatted pre-action with user query replaced
        pre_action_content = self.pre_action_loader.format_pre_action(user_query)
        if not pre_action_content:
            return ""

        # Extract code block from the template (simple regex)
        code_match = re.search(r"```python\n(.*?)\n```", pre_action_content, re.DOTALL)
        if not code_match:
            return ""

        code = code_match.group(1)

        had_error, updated_globals, logs = await async_execute_catch_logs_errors(
            code,
            self.execution_globals,
            runtime=self.execution_runtime,
        )
        logs = logs or "(no output)"

        self._print_indented(f"{Colors.BG_GREEN}{logs}{Colors.RESET}")

        if self.tool_mode_enabled:
            tool_call_id = f"prestep_{uuid.uuid4().hex[:8]}"
            arguments_json = json.dumps({"code": code})
            messages.append({
                "role": "assistant",
                "content": pre_action_content,
                "tool_calls": [
                    {
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": self.tool_function_name,
                            "arguments": arguments_json,
                        },
                    }
                ],
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": self.tool_function_name,
                "content": f"<output>\n{logs}\n</output>",
            })
        else:
            messages.append({"role": "assistant", "content": pre_action_content})
            messages.append({"role": "user", "content": f"<output>\n{logs}\n</output>"})

        return logs

    async def llm_response_action(self, messages: list[dict[str, str]], step_number: int) -> tuple[str, bool]:
        """Stream GPT response and execute code blocks as they complete.

        Returns:
            Tuple of (assistant_content, had_error)
        """
        # Initialize step log
        step_log = StepLog(step_number=step_number)

        # Clean messages before passing to GPT (remove metadata fields)
        clean_messages: list[dict[str, Any]] = []
        for msg in messages:
            filtered: dict[str, Any] = {"role": msg.get("role")}
            if "content" in msg:
                filtered["content"] = msg.get("content")
            if "tool_calls" in msg:
                filtered["tool_calls"] = msg.get("tool_calls")
            if "name" in msg:
                filtered["name"] = msg.get("name")
            if "tool_call_id" in msg:
                filtered["tool_call_id"] = msg.get("tool_call_id")
            clean_messages.append(filtered)

        # Print json indented messages for debugging in yellow
        # print(f"{Colors.RED}Messages to GPT:{Colors.RESET}\n{json.dumps(clean_messages, indent=2)}")

        # Use the AFASAsk GPT class
        gpt = GPT(model=self.model, msg_list=clean_messages)

        stream_observers = []
        dataset_observer = create_dataset_usage_observer(self)
        if dataset_observer:
            stream_observers.append(dataset_observer)

        # Get raw stream
        response_stream = await gpt.get_text_response(
            return_raw_stream=True,
            silent=True,
            stream_observers=stream_observers or None,
            tools=self.tool_specs if self.tool_mode_enabled else None,
            tool_choice=self.tool_choice if self.tool_mode_enabled else None,
        )

        if hasattr(self, "_live_streamer_used"):
            delattr(self, "_live_streamer_used")

        state = StepContainerState()
        live_streamer = None

        shared_ui_msg = getattr(self, "shared_ui_msg", None)
        if shared_ui_msg:
            speed = getattr(getattr(self.config, "ui_streaming", None), "final_answer_speed", 0.001)
            live_streamer = UILiveStreamer(
                shared_ui_msg,
                speed=speed,
                use_grpc=False,
                overwrite=True,
                style_class="interim-response text-gray-500 italic",
            )
            self._live_streamer_used = False

        new_blocks = await self.handle_tokens_stream(step_number, response_stream, state, live_streamer=live_streamer)

        if live_streamer:
            if new_blocks:
                await live_streamer.cancel()
                if getattr(self, "_live_streamer_used", False):
                    await shared_ui_msg.set_content_instantly(
                        "",
                        "content",
                        overwrite=True,
                        skip_grpc=True,
                    )
                self._live_streamer_used = False
            else:
                await live_streamer.finish()

        # Extract output blocks from assistant response
        output_pattern = r"\n<output>\n(.*?)\n</output>\n"

        # Remove output blocks from assistant response
        assistant_response_clean = re.sub(output_pattern, "", state.assistant_content)

        output_text, step_had_error = "", False
        if new_blocks:
            # Execute the FIRST new block and then break to stop streaming
            code, language, _, _ = new_blocks[0]

            # Log the code block

            # Prepare code for execution
            fixed_code = code.strip()

            # Execute code using the restricted runtime
            had_error, updated_globals, logs = await async_execute_catch_logs_errors(
                fixed_code,
                self.execution_globals,
                runtime=self.execution_runtime,
            )

            # If no error, use captured print output
            output = logs or "no output, did you forget to explcitly print values?"

            # Apply token limit if needed
            result, _ = self.token_guard.check_and_limit_output(output)

            # Check if output needs token stats
            token_stats = self.token_guard.get_token_stats(result)

            # Print output in cyan
            self._print_indented(f"{Colors.BG_GREEN}{result}{Colors.RESET}")

            output_text = f"\n<output>\n{result}\n</output>\n"

            # Process and print token usage for this step
            if state.token_usage:
                prompt_tokens, completion_tokens, total_tokens, cached_tokens = update_total_token_usage(self, step_log, state)

                print_step_tokens_used(self, step_number, prompt_tokens, completion_tokens, total_tokens, cached_tokens)

            # Add to session log
            steps = self.session_log.get("steps", [])
            steps.append(step_log)
            self.session_log["steps"] = steps

            # Check if any code block had an error
            step_had_error = any(block.get("had_error", False) for block in step_log.code_blocks if isinstance(block, dict))

        assistant_message: dict[str, Any] = {"role": "assistant"}
        stripped_content = assistant_response_clean.strip()
        if state.tool_call_payload:
            assistant_message["tool_calls"] = [state.tool_call_payload]
            if stripped_content:
                assistant_message["content"] = stripped_content
        else:
            assistant_message["content"] = assistant_response_clean
        self.messages.append(assistant_message)

        if output_text:
            if state.tool_call_payload:
                tool_message = {
                    "role": "tool",
                    "tool_call_id": state.tool_call_payload.get("id"),
                    "name": state.tool_call_payload.get("function", {}).get("name", self.tool_function_name),
                    "content": output_text.strip(),
                }
                self.messages.append(tool_message)
            else:
                self.messages.append({"role": "user", "content": output_text})

        return assistant_response_clean, step_had_error, output_text

    async def handle_tokens_stream(self, step_number, response_stream, state, live_streamer=None):
        new_blocks = []
        tool_mode = self.tool_mode_enabled
        async for chunk in response_stream:  # type: ignore[attr-defined]
            if hasattr(chunk, "usage") and chunk.usage:
                state.token_usage = chunk.usage

            delta = None
            finish_reason = None
            if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                choice = chunk.choices[0]
                finish_reason = getattr(choice, "finish_reason", None)
                delta = getattr(choice, "delta", None)

            content = getattr(delta, "content", None) if delta else None
            if content:
                if state.buffering:
                    state.buffer += content

                    if "\n" in state.buffer and state.buffer.count("```") >= 1:
                        fixed_buffer = state.buffer
                        for lang in state.problematic_languages:
                            fixed_buffer = fixed_buffer.replace(f"```{lang}", "```python")

                        colored = apply_colors(fixed_buffer, state.in_code_block)
                        self._print_indented(colored, end="", flush=True)
                        state.assistant_content += fixed_buffer

                        if fixed_buffer.count("```") % 2 == 1:
                            state.in_code_block = not state.in_code_block

                        state.buffer = ""
                        state.buffering = False

                    elif state.buffer.count("```") >= 2:
                        fixed_buffer = state.buffer
                        for lang in state.problematic_languages:
                            fixed_buffer = fixed_buffer.replace(f"```{lang}", "```python")

                        colored = apply_colors(fixed_buffer, state.in_code_block)
                        self._print_indented(colored, end="", flush=True)
                        state.assistant_content += fixed_buffer

                        state.in_code_block = False
                        state.buffer = ""
                        state.buffering = False
                else:
                    should_buffer = False
                    if "```" in content:
                        for lang in state.problematic_languages:
                            if f"{lang}" in content:
                                should_buffer = True
                                break

                    if should_buffer:
                        state.buffering = True
                        state.buffer = content
                    else:
                        was_in_code_block = state.in_code_block
                        if "```" in content:
                            state.in_code_block = not state.in_code_block

                        colored = apply_colors(content, was_in_code_block)
                        self._print_indented(colored, end="", flush=True)

                        state.assistant_content += content

                        if live_streamer and not was_in_code_block and not state.in_code_block:
                            await live_streamer.enqueue(content)
                            self._live_streamer_used = True

                        if self.stream_steps_to_ui:
                            await stream_step_to_ui(self, step_number, state, content, was_in_code_block)

            if tool_mode:
                tool_calls_delta = getattr(delta, "tool_calls", None) if delta else None
                if tool_calls_delta:
                    for tool_call in tool_calls_delta:
                        call_id = getattr(tool_call, "id", None)
                        if call_id:
                            state.tool_call_id = call_id
                        tool_function = getattr(tool_call, "function", None)
                        if tool_function:
                            name = getattr(tool_function, "name", None)
                            if name:
                                state.tool_call_name = name
                            arguments = getattr(tool_function, "arguments", None)
                            if arguments:
                                state.tool_call_arguments += arguments

                if finish_reason == "tool_calls" and state.tool_call_arguments:
                    try:
                        parsed_args = json.loads(state.tool_call_arguments)
                    except json.JSONDecodeError:
                        continue

                    state.tool_call_args_dict = parsed_args
                    code = parsed_args.get("code", "")

                    if not state.tool_call_id:
                        state.tool_call_id = f"call_{uuid.uuid4().hex[:8]}"
                    if not state.tool_call_name:
                        state.tool_call_name = self.tool_function_name

                    state.tool_call_payload = {
                        "id": state.tool_call_id,
                        "type": "function",
                        "function": {
                            "name": state.tool_call_name,
                            "arguments": state.tool_call_arguments,
                        },
                    }

                    if state.tool_call_arguments:
                        self._print_indented(
                            f"{Colors.CYAN}[TOOL CALL] {state.tool_call_name} arguments:\n{state.tool_call_arguments}{Colors.RESET}"
                        )

                    new_blocks = [(code, "python", 0, 0)]
                    break

                continue

            current_blocks = detect_complete_code_blocks(state.assistant_content)
            new_blocks = current_blocks[state.processed_blocks :]
            if new_blocks:
                if tool_mode and not state.tool_call_payload:
                    code = new_blocks[0][0]
                    state.tool_call_id = f"call_{uuid.uuid4().hex[:8]}"
                    state.tool_call_name = self.tool_function_name
                    state.tool_call_arguments = json.dumps({"code": code})
                    state.tool_call_payload = {
                        "id": state.tool_call_id,
                        "type": "function",
                        "function": {
                            "name": state.tool_call_name,
                            "arguments": state.tool_call_arguments,
                        },
                    }
                    self._print_indented(
                        f"{Colors.CYAN}[TOOL CALL] {state.tool_call_name} arguments (auto-wrapped):\n{state.tool_call_arguments}{Colors.RESET}"
                    )
                break

        return new_blocks


    async def run_conversation(self, user_query: str, max_iterations: int = None) -> list[dict[str, str]]:
        """Run the main conversation loop.

        Args:
            user_query: User's query to process.
            max_iterations: Maximum conversation iterations (uses config default if not provided).

        Returns:
            List of conversation messages.
        """
        # Use config value if max_iterations not provided
        if max_iterations is None:
            max_iterations = self.config.limits.max_iterations

        # Store original user query for step descriptions
        self.original_user_query = user_query

        # Use existing messages or initialize new conversation
        if not self.messages:
            # Initialize new conversation with system prompt from config
            self.messages = [
                {
                    "role": "system",
                    "content": self.config.get_system_prompt(),
                },
                {
                    "role": "user",
                    "content": user_query,
                },
            ]

            # Set context for initial request
            self.request_context = RequestContext.INITIAL
            self.is_follow_up = False

            # Execute pre-actions if configured (only for new conversations)
            await self.execute_pre_actions(self.messages, user_query)

            # Add second step primer if configured (independent of first_step)
            second_step_primer = self.second_step_primer.get_reasoning_primer()
            if second_step_primer:
                # Log the primer so user sees it in logs
                self.logger.info("%s%s%s", Colors.CYAN, second_step_primer, Colors.RESET)

                # Add as partial assistant message that will be completed
                self.messages.append({"role": "assistant", "content": second_step_primer})
        else:
            # Follow-up message - re-apply main system prompt for consistent instruction
            system_prompt = self.config.get_system_prompt()
            if system_prompt:
                self.messages.append({
                    "role": "system",
                    "content": system_prompt,
                })
                self.logger.info("%s[System prompt re-applied for follow-up]%s", Colors.YELLOW, Colors.RESET)

            # Set context for follow-up request
            self.request_context = RequestContext.FOLLOW_UP
            self.is_follow_up = True

            # Add the user message after the refreshed system prompt
            self.messages.append({
                "role": "user",
                "content": f"{user_query}",
            })
            # No pre-actions for follow-ups

        try:
            await ensure_semantic_layer_index(self)
        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.warning("Semantic layer indexing skipped due to error: %s", exc)

        # Main conversation loop
        iteration: int = 0
        total_collapsed_overall = 0

        for iteration in range(max_iterations):
            print("[ITERATION]", iteration, self.request_context.name)
            # Stream response and execute code
            assistant_response, had_error, codelog_output = await self.llm_response_action(self.messages, iteration + 1)

            # Determine if this was a code execution (has <output> tag) vs just reasoning
            has_code_output = bool(codelog_output)

            # Add the ORIGINAL clean response to messages (preserves embed tags)
            # This prevents the system from hallucinating about HTML content

            # Print assistant response in green
            # self._print_indented(f"{Colors.GREEN}{assistant_response}{Colors.RESET}", end="\n", flush=True)

            # === STOP SIGNAL DETECTION ===
            # Four stop conditions apply to ALL request contexts:
            # 1. stop() function call (already sets self.stop_requested)
            # 2. Empty response
            # 3. Text-only response (no code blocks or output) - BUT NOT if it's an error
            # 4. Multiple consecutive text-only responses

            should_stop_signal, stop_reason = should_stop(
                agent=self, iteration=iteration, assistant_response=assistant_response, had_error=had_error, has_code_output=has_code_output
            )

            if should_stop_signal:
                status_message = None
                status_config = getattr(self.config, "status_messages", None)
                if status_config:
                    status_message = getattr(status_config, "before_final_answer", None)
                if not status_message:
                    localization_config = getattr(self.config, "localization", None)
                    if localization_config:
                        status_message = getattr(localization_config, "final_answer_preparing", None)
                await self._status_update(status_message)
                await self._maybe_stream_final_answer(assistant_response, had_error=had_error, has_code_output=has_code_output)
                if hasattr(self, "_live_streamer_used"):
                    delattr(self, "_live_streamer_used")
                break

            # Check for collapsing after EVERY message (we need to track consecutive successes)
            # The collapse function requires N consecutive successful code executions
            if not self.disable_error_collapse:
                collapsed = collapse_error_sequences(
                    self.messages, verbose=False, consecutive_successes_required=self.config.error_collapse.consecutive_successes_required
                )

        # Print final token usage summary
        print_token_summary(self, iteration)

        if not self.final_answer_produced:
            await self._force_final_answer_phase()

        # Save session log (including token usage)
        self.session_log["total_token_usage"] = {
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens_used,
            "cached_tokens": self.total_cached_tokens,
            "steps_count": iteration + 1,
            "average_per_step": self.total_tokens_used // (iteration + 1) if iteration >= 0 else 0,
        }
        _ = self.save_session_log(user_query)

        # Save conversation to both database and Meilisearch before generating suggestions
        # This ensures the conversation is persisted even if suggestions fail or are disabled
        await self.save()

        # Generate suggestions if enabled and this is the main agent (depth 0)
        # This runs at the end of any conversation, regardless of how it ended
        # BUT only if suggestions weren't already generated in the final answer block
        if self.enable_suggestions and self.depth == 0 and not hasattr(self, "_suggestions_generated"):
            # Ensure streaming lock is released before generating suggestions
            if hasattr(self, "shared_ui_msg") and self.shared_ui_msg:
                if (
                    hasattr(self, "final_answer_lock_acquired")
                    and self.final_answer_lock_acquired
                    and hasattr(self.shared_ui_msg, "release_streaming_lock")
                ):
                    lock_released = self.shared_ui_msg.release_streaming_lock(self.final_answer_id)
                    if lock_released:
                        self.logger.debug(
                            "Final answer streaming lock released by %s (end of conversation)",
                            self.final_answer_id,
                        )

            conversation_id = getattr(self, "conversation_id", None)
            if conversation_id:
                self.logger.info("%s[Generating Suggestions]%s", Colors.GREEN, Colors.RESET)

                # Generate and stream suggestions using the current agent instance
                # The agent instance contains all messages and context needed
                suggestion_status = None
                status_config = getattr(self.config, "status_messages", None)
                if status_config:
                    suggestion_status = getattr(status_config, "before_suggestions", None)
                if not suggestion_status:
                    localization_config = getattr(self.config, "localization", None)
                    if localization_config:
                        suggestion_status = getattr(localization_config, "generating_suggestions", None)
                await self._status_update(suggestion_status)
                await generate_and_stream_suggestions(agent_instance=self, conversation_id=conversation_id)

        return self.messages

    async def handle_generate_suggestions(self):
        if self.enable_suggestions and self.depth == 0:
            conversation_id = getattr(self, "conversation_id", None)
            if conversation_id:
                # Generate and stream suggestions using the current agent instance
                # The agent instance contains all messages and context needed
                suggestion_status = None
                status_config = getattr(self.config, "status_messages", None)
                if status_config:
                    suggestion_status = getattr(status_config, "before_suggestions", None)
                if not suggestion_status:
                    localization_config = getattr(self.config, "localization", None)
                    if localization_config:
                        suggestion_status = getattr(localization_config, "generating_suggestions", None)
                await self._status_update(suggestion_status)
                await generate_and_stream_suggestions(agent_instance=self, conversation_id=conversation_id)
                # Mark that suggestions were already generated to avoid duplicates
                self._suggestions_generated = True

    async def _force_final_answer_phase(self) -> None:
        """Request a final textual answer when none has been produced."""

        prev_mode = self.tool_mode_enabled
        prev_context = self.request_context
        try:
            self.tool_mode_enabled = False
            self.request_context = RequestContext.FINAL_ANSWER
            self._inject_final_answer_instruction()
            assistant_response, had_error, codelog_output = await self.llm_response_action(self.messages, 999)
            has_output = bool(codelog_output)
            await self._maybe_stream_final_answer(assistant_response, had_error=had_error, has_code_output=has_output)
        finally:
            self.tool_mode_enabled = prev_mode
            self.request_context = prev_context

    def save_session_log(self, user_query: str) -> str | None:
        """Save the session log to a JSON file.

        Args:
            user_query: Original user query.

        Returns:
            Filename if saved successfully, None otherwise.
        """
        pass

    async def save(self):
        """Saves to db, meilisearch and serializes agent state with dill."""
        if hasattr(self, "conversation_id") and self.conversation_id and hasattr(self, "shared_ui_msg") and self.shared_ui_msg:
            # 1. Save stream events to database
            try:
                self.logger.info("%s[Saving conversation to database]%s", Colors.GREEN, Colors.RESET)
                await self.shared_ui_msg.msg_mngr.save_conversation_to_db(self.conversation_id)
                self.logger.info("%s✓ Conversation saved to database%s", Colors.GREEN, Colors.RESET)
            except Exception as exc:
                self.logger.exception("%sError saving conversation to database: %s%s", Colors.RED, exc, Colors.RESET)

            # 2. Save to Meilisearch for search/sidebar
            if (
                getattr(self.config, "enable_conversation_indexing", False)
                and hasattr(self, "pipeline_session")
                and self.pipeline_session
                and hasattr(self, "user_email")
                and self.user_email
            ):
                try:
                    # Update PipelineSession with final answer before saving to Meilisearch
                    if hasattr(self, "final_answer_accumulator") and self.final_answer_accumulator:
                        final_answer_text = "".join(self.final_answer_accumulator)
                        self.pipeline_session.final_answer = final_answer_text
                        self.logger.info(
                            "%s[Updated PipelineSession with final answer: %s chars]%s",
                            Colors.CYAN,
                            len(final_answer_text),
                            Colors.RESET,
                        )

                    self.logger.info("%s[Saving conversation to Meilisearch]%s", Colors.GREEN, Colors.RESET)
                    await self.pipeline_session.save_to_meilisearch(self.user_email, wait_for_completion=False)
                    self.logger.info("%s✓ Conversation saved to Meilisearch%s", Colors.GREEN, Colors.RESET)
                except Exception as exc:
                    self.logger.exception("%sError saving conversation to Meilisearch: %s%s", Colors.RED, exc, Colors.RESET)

            # 3. Persist agent state for conversation reloads
            try:
                uploaded = await save_agent_state_to_wasabi(self)
                if not uploaded:
                    await save_agent_state(self)
            except Exception as exc:  # pragma: no cover - defensive logging
                self.logger.debug("Agent state serialization failed: %s", exc)


async def main() -> None:
    """Main entry point for CLI usage."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="python -m afasask.fast_streaming_agent.main", description="Run the FastStreamingAgent against a single user query."
    )
    parser.add_argument("query", help="User query to analyse")
    parser.add_argument(
        "--chatconfig",
        help="Chatconfig ID to resolve the agent configuration (overrides FAST_AGENT_CHATCONFIG env variable)",
    )
    parser.add_argument(
        "--config-path",
        dest="config_path",
        help="Explicit path to an agent configuration file (overrides chatconfig resolution)",
    )

    args = parser.parse_args()

    user_query = args.query

    if args.config_path:
        agent_config_path = Path(args.config_path).expanduser()
        path_exists = await asyncio.to_thread(agent_config_path.exists)
        if not path_exists:
            LOGGER.error("Agent configuration not found: %s", agent_config_path)
            sys.exit(1)
        agent_config = str(agent_config_path)
        chatconfig_id = args.chatconfig or "gzb"
    else:
        chatconfig_id = args.chatconfig or os.environ.get("FAST_AGENT_CHATCONFIG") or os.environ.get("CHATCONFIG_ID") or "gzb"
        try:
            agent_config = resolve_agent_config_path_sync(chatconfig_id)
        except FileNotFoundError as exc:
            LOGGER.error("%s", exc)
            sys.exit(1)

    resolved_config_path = str(Path(agent_config).resolve())
    if not has_preloaded_state(resolved_config_path):
        LOGGER.info("Preloaded state missing for %s; performing cold preload (may take a moment).", resolved_config_path)
        try:
            from .preload import preload_agent_state

            await asyncio.to_thread(
                preload_agent_state,
                config_path=resolved_config_path,
                chatconfig_id=chatconfig_id,
                force=False,
            )
        except Exception as exc:
            LOGGER.warning("Preload attempt failed: %s. Proceeding with cold load.", exc)

    # Initialize agent
    agent = FastStreamingAgent(agent_config=resolved_config_path)
    agent.chatconfig_id = chatconfig_id

    # Set conversation_id for standalone script execution to enable suggestions
    agent.conversation_id = f"script_{uuid.uuid4().hex[:8]}"

    final_messages: list[dict[str, str]] | None = None
    # Run conversation
    try:
        final_messages = await agent.run_conversation(user_query)
    except KeyboardInterrupt:
        LOGGER.info("Streaming interrupted by user")
    except Exception:
        LOGGER.exception("Unexpected error while running conversation")
    else:
        if not final_messages:
            final_messages = agent.messages

    # Print the final assistant message (including forked rewrite) for CLI runs
    if final_messages:
        for message in reversed(final_messages):
            if message.get("role") == "assistant" and message.get("content"):
                print("\n===== Final Assistant Message =====\n")
                print(message["content"])
                break


if __name__ == "__main__":
    asyncio.run(main())
