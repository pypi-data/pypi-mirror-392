"""Agent Configuration Module.

Handles loading and validation of FastStreamingAgent configuration from Python, JSON, or YAML files.
Uses Pydantic for type safety and validation.
"""

import json
import yaml
import importlib.util
import sys
import re
from pathlib import Path
from typing import ClassVar, Iterable, Mapping, Optional, Dict, Any, Literal, Union, Callable, Set
from urllib.parse import urlparse

from RestrictedPython.Guards import full_write_guard

try:
    from pydantic import BaseModel, Field, validator
except ImportError:
    from pydantic.v1 import BaseModel, Field, validator


class PreActionConfig(BaseModel):
    """Configuration for pre-action execution."""

    enabled: bool = False
    template: str = ""


class SecondStepConfig(BaseModel):
    """Configuration for second step reasoning primer."""

    enabled: bool = False
    reasoning_template: str = ""


class VerificationStepConfig(BaseModel):
    """Configuration for verification step."""

    enabled: bool = False
    user_message_template: str = "Please verify your answer is correct and complete."


class AgentLimitsConfig(BaseModel):
    """Configuration for agent limits and timeouts."""

    max_subagent_depth: int = 3
    max_iterations: int = 100
    max_output_tokens: int = 20000
    sub_agent_iterations: int = 40


class ErrorCollapseConfig(BaseModel):
    """Configuration for error collapse behavior."""

    enabled: bool = True
    consecutive_successes_required: int = 2


class DutchStepDescriptionConfig(BaseModel):
    """Configuration for Dutch step descriptions."""

    enabled: bool = True
    model: str = "gemini-2.0-flash-thinking-exp"


class FirstStepConfig(BaseModel):
    """Configuration for the first step/pre-action."""

    enabled: bool = False
    template: str = ""


class FunctionConfig(BaseModel):
    """Configuration for a single function available to the agent."""

    name: str
    description: str
    is_async: bool = False  # Whether the function is async and requires await
    module_path: Optional[str] = None  # e.g., "afasask.fast_streaming_agent.fuzzy_search_fallback"
    function_name: Optional[str] = None  # e.g., "fuzzy_search"


class FunctionsConfig(BaseModel):
    """Configuration for functions available to the agent."""

    available_functions: list[FunctionConfig] = Field(
        default_factory=lambda: [FunctionConfig(name="test", description="test() - Prints 'Hello World' for testing", is_async=False)]
    )

    def get_functions_prompt(self) -> str:
        """Generate the prompt text for available functions."""
        if not self.available_functions:
            return ""

        prompt_lines = ["These functions are available in execution globals (no import needed):"]
        for func in self.available_functions:
            await_text = "await " if func.is_async else ""
            async_text = "async function, MUST use await" if func.is_async else "regular function, do NOT use await"
            prompt_lines.append(f"    - `{await_text}{func.description}` - {async_text}")

        return "\n".join(prompt_lines)


def _default_tool_parameters() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Pure Python code to execute inside the AFASAsk restricted runtime.",
            }
        },
        "required": ["code"],
        "additionalProperties": False,
    }


class ToolFunctionSchema(BaseModel):
    """Definition of the tool/function exposed to the LLM when using tool-call mode."""

    name: str = "execute_python"
    description: str = "Voer een python-codeblok uit binnen de AFASAsk sandbox."
    parameters: Dict[str, Any] = Field(default_factory=_default_tool_parameters)

    @validator("name")
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Tool function requires a non-empty name.")
        return trimmed

    @validator("description")
    def validate_description(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Tool function requires a non-empty description.")
        return trimmed


class ExecutionConfig(BaseModel):
    """Controls how the agent executes model instructions (code fences vs tool calls)."""

    mode: Literal["code_blocks", "tool_calls"] = "code_blocks"
    tool_function: ToolFunctionSchema = Field(default_factory=ToolFunctionSchema)

    @validator("mode")
    def validate_mode(cls, value: str) -> str:
        if value not in {"code_blocks", "tool_calls"}:
            raise ValueError("execution.mode must be 'code_blocks' or 'tool_calls'.")
        return value

    def build_tool_spec(self) -> Dict[str, Any]:
        """Return OpenAI-compatible tool definition for tool-call mode."""

        schema = self.tool_function
        return {
            "type": "function",
            "function": {
                "name": schema.name,
                "description": schema.description,
                "parameters": schema.parameters,
            },
        }


class UIStreamingConfig(BaseModel):
    """Configuration for UI streaming behavior."""

    final_answer_speed: float = 0.001
    step_description_speed: float = 0.01
    preview_content_speed: float = 0.0001
    enable_embeds: bool = True


class StreamInsightsConfig(BaseModel):
    """Configuration for streaming-time dataset detection."""

    enabled: bool = False
    emit_base_dataframes: bool = True
    emit_semantic_layers: bool = True
    max_events: int = 25
    icon_class: str = "fa-solid fa-table"


class LocalizationConfig(BaseModel):
    """Configuration for localized text elements."""

    final_answer_preparing: str = "Definitief antwoord wordt opgesteld..."
    analysis_steps_header: str = "Analyse stappen"
    final_answer_complete: str = "✓ Final Answer Complete"
    generating_suggestions: str = "[Generating Suggestions]"
    requesting_detail: str = "[Requesting More Detail]"
    requesting_final_answer: str = "[Preparing Final Answer...]"
    verification_request: str = "[Verification Request]"


class WebUIConfig(BaseModel):
    """Configuration for web UI layout toggles."""

    show_sidebar: bool = False
    collapse_markdown_h2: bool = True


class SystemPromptConfig(BaseModel):
    """Configuration for the main system prompt."""

    # Full prompt can override everything if provided
    full_prompt: Optional[str] = None

    # Individual components (used if full_prompt is not provided) - defaults to no config message
    role_description: str = "You are an assistant in default mode with no config loaded."
    goal: str = "Please load a configuration file to get proper instructions."
    response_format_instructions: str = "No formatting instructions loaded from config."

    # Core instructions - defaults to minimal instructions
    core_instructions: list[str] = Field(default_factory=lambda: ["No specific instructions loaded from configuration file."])

    database_context: str = "No database context loaded from config."


class UserFollowsUpSysPromptConfig(BaseModel):
    """Configuration for the system prompt injected before user follow-up messages."""

    full_prompt: Optional[str] = None


class RuntimeSecurityConfig(BaseModel):
    """Configuration for sandbox behaviour of the execution runtime."""

    mode: Literal["strict", "lenient"] = "strict"
    extra_allowed_imports: list[str] = Field(default_factory=list)
    blocked_imports: list[str] = Field(default_factory=list)
    enable_open_builtin: bool = False

    LENIENT_BASE_IMPORTS: ClassVar[tuple[str, ...]] = (
        "numpy",
        "pandas",
        "pathlib",
        "typing",
        "random",
        "statistics",
    )

    def build_runtime_options(
        self,
        base_allowed_imports: Iterable[str],
        base_additional_builtins: Mapping[str, Any],
    ) -> tuple[tuple[str, ...], dict[str, Any], Callable[[Any], Any], bool]:
        """Return the allowed imports and additional builtins for the runtime."""

        allowed = list(dict.fromkeys(base_allowed_imports))

        if self.mode == "lenient":
            for module in self.LENIENT_BASE_IMPORTS:
                if module not in allowed:
                    allowed.append(module)

        for module in self.extra_allowed_imports:
            if module not in allowed:
                allowed.append(module)

        if self.blocked_imports:
            blocked_set = set(self.blocked_imports)
            allowed = [module for module in allowed if module not in blocked_set]

        additional_builtins = dict(base_additional_builtins)
        if self.enable_open_builtin:
            additional_builtins.setdefault("open", open)

        write_guard: Callable[[Any], Any] = full_write_guard
        if self.mode == "lenient":

            def allow_all_write_guard(obj: Any) -> Any:
                return obj

            write_guard = allow_all_write_guard

        enable_restrictions = self.mode != "lenient"

        return tuple(allowed), additional_builtins, write_guard, enable_restrictions


def _canonicalize_dataframe_name(name: str) -> Set[str]:
    """Return canonical aliases for dataframe name matching."""
    aliases: set[str] = set()
    if not name:
        return aliases

    trimmed = name.strip()
    if not trimmed:
        return aliases

    lowered = trimmed.lower()
    aliases.add(lowered)

    path = Path(trimmed)
    if path.name:
        aliases.add(path.name.lower())
        aliases.add(path.stem.lower())

    sanitised = re.sub(r"\W+", "_", path.stem if path.stem else trimmed).strip("_")
    if sanitised:
        aliases.add(sanitised.lower())

    return aliases


class DataFramePathConfig(BaseModel):
    """Explicit path mapping for dataframe sources."""

    name: str
    path: str | None = None
    local_path: str | None = None
    remote_path: str | None = None

    @validator("name")
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Dataframe path configuration requires a non-empty name.")
        return trimmed

    def candidate_paths(self) -> list[str]:
        """Return a prioritized list of candidate filesystem paths."""
        candidates: list[str] = []
        for value in (self.path, self.local_path, self.remote_path):
            if value and value not in candidates:
                candidates.append(value)
        return candidates


class DataFrameLoadSettings(BaseModel):
    """Configuration for loading dataframes into the agent runtime."""

    format: Literal["polars", "pandas"] = "polars"
    paths: list[Union[str, DataFramePathConfig]] = Field(default_factory=list)

    @validator("paths", pre=True)
    def coerce_paths(cls, value):
        """Ensure path definitions are parsed into supported objects."""
        if not isinstance(value, list):
            raise ValueError("dataframes_to_load.paths must be a list")

        parsed: list[Union[str, DataFramePathConfig]] = []
        for entry in value:
            if isinstance(entry, DataFramePathConfig):
                parsed.append(entry)
            elif isinstance(entry, dict):
                parsed.append(DataFramePathConfig(**entry))
            else:
                parsed.append(str(entry))
        return parsed

    def normalized_paths(self) -> list[str]:
        """Backward compatible list of dataframe names."""
        return [entry.name if isinstance(entry, DataFramePathConfig) else str(entry) for entry in self.paths]

    def normalized_sources(self) -> list[dict[str, Any]]:
        """Return dataframe sources with their candidate paths."""
        sources: list[dict[str, Any]] = []
        for entry in self.paths:
            if isinstance(entry, DataFramePathConfig):
                sources.append({
                    "logical_name": entry.name,
                    "candidates": entry.candidate_paths(),
                })
            else:
                sources.append({
                    "logical_name": str(entry),
                    "candidates": [],
                })
        return sources


class SemanticLayerDefinition(BaseModel):
    """Declarative definition for a semantic-layer dataframe."""

    name: str
    description: str
    code: str
    dependencies: list[str] = Field(default_factory=list)
    enabled: bool = True

    @validator("name")
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Semantic layer definition requires a non-empty name.")
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", trimmed):
            raise ValueError(
                f"Invalid semantic layer name '{value}'. Use snake_case alphanumeric identifiers (letters, numbers, underscores)."
            )
        return trimmed

    @validator("description")
    def validate_description(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Semantic layer definition requires a non-empty description.")
        return value.strip()

    @validator("code")
    def validate_code(cls, value: str) -> str:
        code = value.strip()
        if not code:
            raise ValueError("Semantic layer definition must include executable code that assigns `result`.")
        if "result" not in code or not re.search(r"\bresult\s*=", code):
            raise ValueError("Semantic layer code must assign the transformed dataframe to a variable named 'result'.")
        return code


class SemanticLayerConfig(BaseModel):
    """Container for semantic layer configuration."""

    definitions: list[SemanticLayerDefinition] = Field(default_factory=list)

    @validator("definitions")
    def ensure_unique_names(cls, definitions: list[SemanticLayerDefinition]) -> list[SemanticLayerDefinition]:
        seen: Set[str] = set()
        for definition in definitions:
            key = definition.name.strip().lower()
            if key in seen:
                raise ValueError(f"Duplicate semantic layer name detected: {definition.name!r}")
            seen.add(key)
        return definitions


class DataFramePreprocessOperation(BaseModel):
    """Executable preprocessing step applied to a dataframe immediately after loading."""

    name: str
    target: str
    description: str = ""
    code: str
    enabled: bool = True

    @validator("name")
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Preprocess operation requires a non-empty name.")
        return trimmed

    @validator("target")
    def validate_target(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Preprocess operation target cannot be empty.")
        return trimmed

    @validator("code")
    def validate_code(cls, value: str) -> str:
        code = value.strip()
        if not code:
            raise ValueError("Preprocess operation code cannot be empty.")
        return code

    def canonical_targets(self) -> Set[str]:
        return _canonicalize_dataframe_name(self.target)


class MultiStepConfig(BaseModel):
    """Configuration for the multi-step analysis process."""

    detail_request_enabled: bool = True
    detail_request_message: str = "No detail request message loaded from config. Agent is in default mode."

    final_answer_enabled: bool = True
    final_answer_message: str = "No final answer message loaded from config. Agent is in default mode."


class ForkDefinitionConfig(BaseModel):
    """Configuration for a single forked response."""

    enabled: bool = False
    trigger: str = ""
    model: Optional[str] = None
    system_prompt: str = ""
    user_prompt: str = ""
    append_to_last_assistant: bool = False
    newline_prefix: str = "\n\n"
    stream_target: Optional[str] = None


class AgentConfig(BaseModel):
    """Complete configuration for FastStreamingAgent."""

    # Model configuration
    model: str = "gpt-4"  # Default model for main reasoning
    suggestions_model: str = "gpt-4"  # Model for generating suggestions (can be different/cheaper)

    # Dataframes to load for this agent (subset of available dataframes)
    # Can include both file-based names and database URLs
    dataframes_to_load: Union[list[str], DataFrameLoadSettings] = Field(
        default_factory=lambda: [
            "financial_mutations",
            "relations",
            "interactions",
            "communications",
            "contacts_dossiers",
            "subscriptions",
        ]
    )
    dataframe_preprocessors: list[DataFramePreprocessOperation] = Field(default_factory=list)

    @validator("dataframes_to_load", pre=True)
    def validate_dataframe_sources(cls, v):
        """Validate dataframe sources including database URLs."""
        if isinstance(v, dict):
            return DataFrameLoadSettings(**v)
        if isinstance(v, DataFrameLoadSettings):
            return v
        if not isinstance(v, list):
            raise ValueError("dataframes_to_load must be a list or mapping")

        for item in v:
            if not isinstance(item, str):
                raise ValueError(f"Each dataframe source must be a string, got: {type(item)}")

            # Check if it's a database URL
            if item.startswith(("postgresql://", "postgres://", "postgresql+asyncpg://")):
                # Validate database URL format
                cls._validate_database_url(item)
            # If not a database URL, assume it's a regular dataframe name
            # (validation for regular names happens during loading)

        return v

    def get_dataframe_load_settings(self) -> DataFrameLoadSettings:
        """Return dataframe loading settings in normalized form."""
        if isinstance(self.dataframes_to_load, DataFrameLoadSettings):
            return self.dataframes_to_load
        return DataFrameLoadSettings(paths=list(self.dataframes_to_load))

    def get_semantic_layer_definitions(self) -> list[SemanticLayerDefinition]:
        """Return all enabled semantic layer definitions."""
        return [definition for definition in self.semantic_layer.definitions if definition.enabled]

    def get_preprocessors_for(self, logical_name: str) -> list[DataFramePreprocessOperation]:
        """Return enabled preprocessors matching the provided dataframe name."""
        if not logical_name:
            return []
        canonical = _canonicalize_dataframe_name(logical_name)
        if not canonical:
            return []

        matching: list[DataFramePreprocessOperation] = []
        for operation in self.dataframe_preprocessors:
            if not operation.enabled:
                continue
            if canonical & operation.canonical_targets():
                matching.append(operation)
        return matching

    @staticmethod
    def _validate_database_url(url: str) -> None:
        """Validate database URL format."""
        # Check for table name delimiter
        if "#" not in url:
            raise ValueError(f"Database URL must include table name after '#'. Format: postgresql://user:pass@host:port/dbname#table_name")

        connection_part, table_part = url.rsplit("#", 1)

        # Validate connection URL structure
        try:
            parsed = urlparse(connection_part)
            if not parsed.scheme:
                raise ValueError(f"Invalid database URL scheme: {connection_part}")
            if not parsed.netloc:
                raise ValueError(f"Invalid database URL netloc: {connection_part}")
        except Exception as e:
            raise ValueError(f"Invalid database URL format: {e}")

        # Validate table name (basic SQL identifier validation, supports schema.table format)
        # Allow: identifier or schema.identifier (with optional dots for multi-level schemas)
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$", table_part):
            raise ValueError(
                f"Invalid table name: {table_part}. "
                f"Table names must be valid SQL identifiers (letters, numbers, underscore, starting with letter/underscore). "
                f"Schema-qualified names like 'schema.table' are supported."
            )

    # Existing configuration sections (backward compatibility)
    enabled: bool = True  # For backward compatibility
    template: str = ""  # Deprecated - use first_step.template instead
    first_step: FirstStepConfig = Field(default_factory=FirstStepConfig)
    second_step: SecondStepConfig = Field(default_factory=SecondStepConfig)
    verification_step: VerificationStepConfig = Field(default_factory=VerificationStepConfig)
    runtime_security: RuntimeSecurityConfig = Field(default_factory=RuntimeSecurityConfig)

    # Configuration sections with defaults
    limits: AgentLimitsConfig = Field(default_factory=AgentLimitsConfig)
    error_collapse: ErrorCollapseConfig = Field(default_factory=ErrorCollapseConfig)
    dutch_step_descriptions: DutchStepDescriptionConfig = Field(default_factory=DutchStepDescriptionConfig)
    ui_streaming: UIStreamingConfig = Field(default_factory=UIStreamingConfig)
    stream_insights: StreamInsightsConfig = Field(default_factory=StreamInsightsConfig)
    localization: LocalizationConfig = Field(default_factory=LocalizationConfig)
    web_ui: WebUIConfig = Field(default_factory=WebUIConfig)
    system_prompt: SystemPromptConfig = Field(default_factory=SystemPromptConfig)
    user_follows_up_sys_prompt: UserFollowsUpSysPromptConfig = Field(default_factory=UserFollowsUpSysPromptConfig)
    multi_step: MultiStepConfig = Field(default_factory=MultiStepConfig)
    forked_responses: Dict[str, ForkDefinitionConfig] = Field(default_factory=dict)
    functions: FunctionsConfig = Field(default_factory=FunctionsConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    semantic_layer: SemanticLayerConfig = Field(default_factory=SemanticLayerConfig)

    # Agent behavior settings
    enable_suggestions: bool = True
    load_state_dataframes: bool = True
    enable_state_serialization: bool = False
    enable_conversation_indexing: bool = False

    @classmethod
    def from_json_file(cls, config_path: str | Path) -> "AgentConfig":
        """Load configuration from JSON file.

        Args:
            config_path: Path to JSON configuration file.

        Returns:
            AgentConfig instance with loaded configuration.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            ValueError: If JSON is invalid or doesn't match schema.
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            return cls(**config_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file {config_path}: {e}")
        except Exception as e:
            raise ValueError(f"Invalid configuration in {config_path}: {e}")

    @classmethod
    def from_python_file(cls, config_path: str | Path) -> "AgentConfig":
        """Load configuration from Python file.

        Args:
            config_path: Path to Python configuration file.

        Returns:
            AgentConfig instance with loaded configuration.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            ValueError: If Python file doesn't contain AGENT_CONFIG.
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config file not found: {config_path}")

        try:
            # Load the Python module dynamically
            spec = importlib.util.spec_from_file_location("agent_config_module", config_path)
            if spec is None or spec.loader is None:
                raise ValueError(f"Could not load Python module from {config_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules["agent_config_module"] = module
            spec.loader.exec_module(module)

            # Get the AGENT_CONFIG dictionary
            if not hasattr(module, "AGENT_CONFIG"):
                raise ValueError(f"Python config file {config_path} must contain an AGENT_CONFIG dictionary")

            config_data = module.AGENT_CONFIG
            return cls(**config_data)
        except Exception as e:
            raise ValueError(f"Invalid Python configuration in {config_path}: {e}")

    @classmethod
    def from_yaml_file(cls, config_path: str | Path) -> "AgentConfig":
        """Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file.

        Returns:
            AgentConfig instance with loaded configuration.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            ValueError: If configuration is invalid.
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config file not found: {config_path}")

        try:
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
            return cls(**config_data)
        except Exception as e:
            raise ValueError(f"Invalid YAML configuration in {config_path}: {e}")

    @classmethod
    def from_file(cls, config_path: str | Path) -> "AgentConfig":
        """Load configuration from Python, JSON, or YAML file based on extension.

        Args:
            config_path: Path to configuration file (.py, .json, .yaml, or .yml).

        Returns:
            AgentConfig instance with loaded configuration.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            ValueError: If file format is unsupported or invalid.
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Agent config file not found: {config_path}")

        if config_path.suffix == ".py":
            return cls.from_python_file(config_path)
        elif config_path.suffix == ".json":
            return cls.from_json_file(config_path)
        elif config_path.suffix in [".yaml", ".yml"]:
            return cls.from_yaml_file(config_path)
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}. Use .py, .json, .yaml, or .yml")

    @classmethod
    def create_default(cls) -> "AgentConfig":
        """Create a default configuration instance.

        Returns:
            AgentConfig with all default values.
        """
        return cls()

    def to_json_file(self, config_path: str | Path) -> None:
        """Save configuration to JSON file.

        Args:
            config_path: Path where to save the configuration.
        """
        config_path = Path(config_path)
        config_data = self.dict(exclude_unset=False)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def get_system_prompt(self) -> str:
        """Generate the complete system prompt from configuration.

        Returns:
            Complete system prompt string ready for use.
        """
        # If full_prompt is provided, use it directly
        if self.system_prompt.full_prompt:
            return self.system_prompt.full_prompt

        # Otherwise, build from components
        prompt_parts = [
            f"{self.system_prompt.role_description} {self.system_prompt.goal}",
            "",
            self.system_prompt.response_format_instructions,
            "",
            "IMPORTANT INSTRUCTIONS:",
        ]

        # Add numbered instructions
        for i, instruction in enumerate(self.system_prompt.core_instructions, 1):
            prompt_parts.append(f"{i}. {instruction}")

        # Add function documentation from config
        functions_prompt = self.functions.get_functions_prompt()
        if functions_prompt:
            prompt_parts.append(f"16. {functions_prompt}")

        prompt_parts.extend([
            "Execute code blocks to:",
            "- Explore data and understand the problem",
            "- Perform calculations and analysis",
            "- Generate insights and conclusions",
            "- Create visualizations if helpful",
            "",
            self.system_prompt.database_context,
            "",
            "Be methodical and thorough. Each code block should move you closer to solving the user's request.",
        ])

        return "\n".join(prompt_parts)

    def get_user_follows_up_system_prompt(self) -> Optional[str]:
        """Get the system prompt to inject before user follow-up messages.

        Returns:
            System prompt string if configured, None otherwise.
        """
        system_prompt = self.get_system_prompt()
        return system_prompt if system_prompt else None

    def __str__(self) -> str:
        """String representation showing key configuration settings."""
        return (
            f"AgentConfig("
            f"pre_action={'enabled' if self.enabled else 'disabled'}, "
            f"max_subagent_depth={self.limits.max_subagent_depth}, "
            f"max_iterations={self.limits.max_iterations}, "
            f"suggestions={'enabled' if self.enable_suggestions else 'disabled'}"
            f")"
        )
