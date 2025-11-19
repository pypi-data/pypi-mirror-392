import json
import os
from typing import TYPE_CHECKING, Any

import openai

try:
    from .prompt_loader import Prompts
except ImportError:
    # Create a simple Prompts class for environments where the relative import isn't available
    class Prompts:  # type: ignore[too-many-ancestors]
        def __init__(self, sys=None, user=None, parse_sys=None, parse_user=None, parse_schema=None, images=None) -> None:
            self.sys = sys
            self.user = user
            self.parse_sys = parse_sys
            self.parse_user = parse_user
            self.parse_schema = parse_schema
            self.images = images


import logging

import httpx
import tiktoken
from rich import print

from .fallback_gpt_models import use_fall_back_on_fail

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class CustomAsyncHTTPClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.pop("proxies", None)  # Remove the 'proxies' argument if present
        # Add referrer headers for Google API compatibility
        headers = kwargs.get("headers", {})
        headers.update({"Referer": "https://afasask.gzb.nl", "User-Agent": "AFASAsk-Server/1.0"})
        kwargs["headers"] = headers
        super().__init__(*args, **kwargs)

    async def request(self, method, url, **kwargs):
        """Override request method to ensure referrer headers are always included."""
        # Ensure our referrer headers are always present
        headers = kwargs.get("headers", {})
        headers = headers.copy() if isinstance(headers, dict) else dict(headers) if headers else {}

        # Add referrer headers for Google API compatibility
        headers.update({"Referer": "https://afasask.gzb.nl", "User-Agent": "AFASAsk-Server/1.0"})
        kwargs["headers"] = headers

        return await super().request(method, url, **kwargs)


# my_class.py


logger = logging.getLogger(__name__)


class GPT:
    """A utility class for interacting with OpenAI's GPT-based models, supporting direct user queries, tool invocation, and tool selection.

    This class allows for different modes of interaction with the GPT model:
    - Direct textual responses.
    - Function (tool) invocation with a specific schema.
    - Selection among multiple tools based on context.
    - Processing images along with text (multimodal capabilities).

    Image Support:
    The class supports multimodal input with images. Images should be provided as a list of dictionaries
    with the following format:

    images = [
        {
            "url": "data:image/png;base64,<base64_encoded_image>",
            "detail": "auto"  # or "low" or "high"
        }
    ]

    Example usage with images:
    ```python
    import base64

    # Read and encode image
    with open("screenshot.png", "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    images = [{"url": f"data:image/png;base64,{image_data}", "detail": "auto"}]

    gpt = GPT(
        sys_msg="You are a helpful assistant that can analyze images.",
        user_msg="Describe what you see in this image.",
        images=images,
        model="gpt-4o"
    )

    response, _, _ = await gpt.run()
    ```

    Model Compatibility:
    - ✅ Full image support: gpt-4o, gpt-4o-mini, gemini-2.0-flash, gemini-2.0-flash-lite, deepseek/deepseek-r1
    - ❌ No image support: llama-3.3-70b-versatile, llama-3.1-8b-instant, llama-3.1-70b-versatile, etc.
    - Note: Models without image support will fail when images are provided

    Attributes:
        client (openai.OpenAI): The OpenAI client used for API calls.
        msg_list (list[dict]): A list of messages formatted for the OpenAI API.
        function_call_schema (dict, optional): A specific schema for a function call.
        function_call_schema_list (list[dict], optional): A list of schemas for multiple function calls.
        model (str): The model to use, defaulting to "gpt-4o".
        images (List[Dict[str, Any]], optional): List of image objects for multimodal input.

    Methods:
        construct_msg_list(sys_msg: str, user_msg: str) -> list[dict]:
            Constructs the message list from system and user messages.

        construct_multimodal_msg_list(sys_msg: str, user_msg: str, images: List[Dict]) -> list[dict]:
            Constructs a multimodal message list with both text and images.

        get_tool_response() -> dict:
            Executes a specific tool call based on the provided schema and returns the arguments.

        select_tool() -> tuple[str, dict]:
            Allows the model to select a tool from a list of schemas and returns the selected tool's name and arguments.

        get_text_response() -> str:
            Gets a streamed textual response from the model, printing it chunk by chunk.

        run() -> Union[str, tuple[str, dict], dict]:
            Determines the interaction mode (textual response, single tool, or tool selection) and executes accordingly.
    """

    def __init__(
        self,
        sys_msg: str | None = None,
        user_msg: str | None = None,
        function_call_schema: dict | None = None,
        function_call_schema_list: list[dict] | None = None,
        msg_list: list[dict] | None = None,
        stream: bool = False,
        model="gpt-4o",
        prompts: Prompts = None,
        images: list[dict[str, Any]] | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize the GPT instance.

        Args:
            sys_msg (str, optional): System message to set context for the AI.
            user_msg (str, optional): User message/query.
            function_call_schema (dict, optional): Schema for a specific function call.
            function_call_schema_list (list[dict], optional): List of schemas for multiple function calls.
            msg_list (list[dict], optional): Pre-constructed message list (overrides sys_msg/user_msg).
            stream (bool, optional): Whether to stream responses. Defaults to False.
            model (str, optional): Model to use. Defaults to "gpt-4o".
            prompts (Prompts, optional): Prompts object containing sys, user, and parse configurations.
            images (List[Dict[str, Any]], optional): List of image objects for multimodal input.
                Each image should be a dict with:
                - "url": data URL with base64 encoded image (e.g., "data:image/png;base64,...")
                - "detail": "auto", "low", or "high" (optional, defaults to "auto")
        """
        self.prompts = None
        self.images = images
        if prompts:
            self.prompts = prompts
            sys_msg = prompts.sys
            user_msg = prompts.user
            if prompts.parse_schema:
                function_call_schema = prompts.parse_schema

        # Use multimodal message construction if images are provided
        if self.images:
            self.msg_list = self.construct_multimodal_msg_list(sys_msg, user_msg, self.images)
        else:
            self.msg_list = self.construct_msg_list(sys_msg, user_msg)

        self.fallback_mapping = {
            "gemini-2.0-flash": "gemini-2.0-flash-lite",
            "gemini-2.0-flash-lite": "gpt-4o-mini",
            "gpt-4o": "gpt-4o-mini",
        }

        # Overwrite the message list if it is explicitly given
        if msg_list:
            self.msg_list = msg_list

        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except Exception:
            self.encoder = tiktoken.encoding_for_model("gpt-4o")

        self.function_call_schema = function_call_schema
        self.function_call_schema_list = function_call_schema_list

        self.max_prompt_tokens = 64000

        self.model = model
        self.stream = stream
        self.api_key_override = api_key

        self.initialize_client()

    def supports_images(self) -> bool:
        """Check if the current model supports image inputs."""
        image_supported_models = [
            "gpt-4o",
            "gpt-4o-mini",
            "o3-mini",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "deepseek/deepseek-r1",
            "anthropic/claude-sonnet-4",
        ]
        return self.model in image_supported_models

    def get_referrer_headers(self) -> dict:
        """Get referrer headers for Google API compatibility."""
        return {"Referer": "https://afasask.gzb.nl", "User-Agent": "AFASAsk-Server/1.0"}

    def initialize_client(self) -> None:
        # Define referrer headers for Google API compatibility
        referrer_headers = {"Referer": "https://afasask.gzb.nl", "User-Agent": "AFASAsk-Server/1.0"}
        azure_api_key = self.api_key_override or os.getenv("AZURE_OPENAI_API_KEY")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

        def _azure_endpoint(var_name: str, fallback: str | None = None) -> str:
            endpoint = os.getenv(var_name) or (os.getenv(fallback) if fallback else None)
            if not endpoint:
                raise RuntimeError(f"{var_name} must be set to call Azure model {self.model}.")
            return endpoint

        def _azure_client(endpoint: str, api_version: str | None = None) -> openai.AsyncAzureOpenAI:
            if not azure_api_key:
                raise RuntimeError("Set AZURE_OPENAI_API_KEY (or pass api_key) to use Azure-hosted OpenAI models.")
            return openai.AsyncAzureOpenAI(
                api_key=azure_api_key,
                azure_endpoint=endpoint,
                api_version=api_version or azure_api_version,
                http_client=CustomAsyncHTTPClient(),
                default_headers=referrer_headers,
            )

        if self.model == "gpt-4o":
            endpoint = _azure_endpoint("AZURE_OPENAI_GPT4O_ENDPOINT")
            self.client = _azure_client(endpoint)
        elif self.model == "gpt-4o-mini":
            endpoint = _azure_endpoint("AZURE_OPENAI_GPT4O_MINI_ENDPOINT", "AZURE_OPENAI_GPT4O_ENDPOINT")
            self.client = _azure_client(endpoint)
        elif self.model in {
            "llama-3.3-70b-versatile",
            "llama-3.3-70b-specdec",
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "llama3-8b-8192",
            "llama3-70b-8192",
        }:
            # Run with Groq for fast Llama models - check this first before OpenRouter
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise RuntimeError("Set GROQ_API_KEY to call Groq-hosted models.")
            self.client = openai.AsyncOpenAI(
                api_key=groq_api_key,
                base_url="https://api.groq.com/openai/v1",
                http_client=CustomAsyncHTTPClient(),
                default_headers=referrer_headers,
            )
        elif self.model in {"deepseek/deepseek-r1", "anthropic/claude-sonnet-4"}:
            # Run with OpenRouter for other models
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            if not openrouter_api_key:
                raise RuntimeError("Set OPENROUTER_API_KEY to call OpenRouter-hosted models.")
            self.client = openai.AsyncOpenAI(
                api_key=openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                http_client=CustomAsyncHTTPClient(),
                default_headers=referrer_headers,
            )
        elif self.model in {"gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash", "gemini-2.5-flash-lite"}:
            api_key = (
                self.api_key_override
                or os.getenv("GEMINI_API_KEY_GENERAL")
                or os.getenv("GEMINI_API_KEY")
            )
            if not api_key:
                raise RuntimeError("Set GEMINI_API_KEY_GENERAL (or GEMINI_API_KEY) to use Gemini models via GPT helper.")

            self.client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=os.getenv("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
                http_client=CustomAsyncHTTPClient(),
                default_headers=referrer_headers,
            )
        elif self.model == "o3-mini":
            endpoint = _azure_endpoint("AZURE_OPENAI_O3_ENDPOINT")
            self.client = _azure_client(endpoint)
        else:
            raise RuntimeError(f"Model {self.model} is not configured. Provide the proper env vars or extend initialize_client().")

    def construct_msg_list(self, sys_msg: str, user_msg: str) -> list[dict]:
        """Given system message and user message string, constructs the messages list for OpenAI API."""
        sys = {"role": "system", "content": sys_msg}
        user = {"role": "user", "content": user_msg}
        return [sys, user]

    def construct_multimodal_msg_list(self, sys_msg: str, user_msg: str, images: list[dict[str, Any]] | None = None) -> list[dict]:
        """Constructs a multimodal message list with both text and images."""
        sys = {"role": "system", "content": sys_msg}

        # If there are no images, return standard message list
        if not images:
            user = {"role": "user", "content": user_msg}
            return [sys, user]

        # Create content array for multimodal message
        content = [{"type": "text", "text": user_msg}]

        # Add images to content
        content.extend({"type": "image_url", "image_url": {"url": image["url"], "detail": image.get("detail", "auto")}} for image in images)

        user = {"role": "user", "content": content}
        return [sys, user]

    @use_fall_back_on_fail
    async def get_tool_response(self, func_call_schema: dict | None = None, msg_list: list[dict] | None = None) -> dict:
        """Executes a specific tool call based on the provided schema and returns the arguments."""
        if not func_call_schema:
            func_call_schema = self.function_call_schema

        if not msg_list:
            msg_list = self.msg_list

        response = await self.client.chat.completions.create(
            model="gemini-2.0-flash-lite",  # Ugly hack, current provider might be openai while we try to use gemin, however, now all parsing will be much fater which previously was very slow
            messages=msg_list,
            stream=self.stream,
            tools=[func_call_schema],
            tool_choice=func_call_schema,
            extra_headers=self.get_referrer_headers(),
        )

        tool_call = response.choices[0].message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        return response, tool_name, tool_args

    @use_fall_back_on_fail
    async def select_tool(self) -> dict:
        """Allows the model to select a tool from a list of schemas and returns the selected tool's name and arguments.

        Returns:
            tuple[str, dict]: The name of the selected tool and its arguments.
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.msg_list,
            stream=self.stream,
            tools=self.function_call_schema_list,
            extra_headers=self.get_referrer_headers(),
        )

        try:
            tool_call = response.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            return response, function_name, tool_args
        except Exception as e:
            print("tool selection error")
            print(e)
            return None, None

    @use_fall_back_on_fail
    async def get_text_response(self, return_raw_stream=False, silent=True, msg_list: list[dict] | None = None) -> "str | AsyncGenerator":
        """Gets a streamed textual response from the model, printing it chunk by chunk.

        Returns:
            str: The full response text.
            AsyncGenerator: The raw response stream. (if return_raw_stream=True)
        """
        if not msg_list:
            msg_list = self.msg_list

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=msg_list,
            stream=True,
            stream_options={"include_usage": True},
            extra_headers=self.get_referrer_headers(),
        )

        if return_raw_stream:
            return response

        # Print the chunks of the response and add them to the full message
        full_msg = ""

        async for chunk in response:
            if len(chunk.choices) == 0:
                continue
            if chunk and chunk.choices[0].delta.content:
                if not silent:
                    print(chunk.choices[0].delta.content, end="", flush=True)
                full_msg += chunk.choices[0].delta.content

        # Add the response to the message list
        self.msg_list.append({"role": "assistant", "content": full_msg})

        return full_msg

    async def run(
        self,
        silent=True,
        return_raw_stream=False,
        sys_msg: str | None = None,
        user_msg: str | None = None,
        function_call_schema: dict | None = None,
        prompts: Prompts = None,
    ):
        """Determines the interaction mode (textual response, single tool, or tool selection) and executes accordingly.

        Returns:
            Always returns a tuple of length 3, (response, tool_name, tool_args)
            But the tool_name and tool_args might be empty.
        """
        if prompts:
            # We want to trim the prompts very close to the actual LLM call itself
            prompts = await self.trim_prompts(prompts)
        elif self.prompts:
            prompts = await self.trim_prompts(self.prompts)

        if self.function_call_schema_list:
            return await self.select_tool()
        # Check if we have images to process - either from prompts object or direct images parameter
        has_images = (prompts and hasattr(prompts, "images") and prompts.images) or self.images

        # If images are provided but model doesn't support them, log warning and fall back to text-only
        if has_images and not self.supports_images():
            logger.warning(f"Model {self.model} doesn't support images. Falling back to text-only mode.")
            has_images = False

        if has_images:
            # Use multimodal message construction for images
            if prompts:
                msg_list = self.construct_multimodal_msg_list(prompts.sys, prompts.user, prompts.images)
            else:
                # Use the already constructed multimodal message list from __init__
                msg_list = self.msg_list
        # Use standard message construction
        elif prompts:
            msg_list = self.construct_msg_list(prompts.sys, prompts.user)
        # For models that don't support images, reconstruct as text-only
        elif self.images and not self.supports_images():
            # Extract text from the original parameters and create text-only message
            # We need to find the original sys_msg and user_msg
            sys_content = self.msg_list[0]["content"] if self.msg_list else ""
            user_content = self.msg_list[1]["content"]
            if isinstance(user_content, list):
                # Extract just the text part from multimodal content
                user_text = next((item["text"] for item in user_content if item["type"] == "text"), "")
                msg_list = self.construct_msg_list(sys_content, user_text)
            else:
                msg_list = self.msg_list
        else:
            # Use the already constructed message list from __init__
            msg_list = self.msg_list

        # If function_call_schema is provided, use structured output
        if self.function_call_schema or (prompts and prompts.parse_schema):
            if prompts and prompts.parse_sys and prompts.parse_user:
                # Two-step: get text response then parse it
                response = await self.get_text_response(silent=silent, return_raw_stream=False, msg_list=msg_list)
                if not getattr(prompts, "skip_sys", False):
                    prompts.parse_sys = prompts.parse_sys.format(previous_response=response)
                prompts.parse_user = prompts.parse_user.format(previous_response=response)
                parse_msg_list = self.construct_msg_list(prompts.parse_sys, prompts.parse_user)
                tool_response, tool_name, tool_arg = await self.get_tool_response(
                    msg_list=parse_msg_list, func_call_schema=prompts.parse_schema
                )
                return response, tool_name, tool_arg
            # Direct function calling with current message
            tool_response, tool_name, tool_args = await self.get_tool_response(
                func_call_schema=self.function_call_schema, msg_list=msg_list
            )
            return tool_response, tool_name, tool_args

        response = await self.get_text_response(silent=silent, return_raw_stream=return_raw_stream, msg_list=msg_list)
        return response, None, None

    async def trim_prompts(self, prompts):
        # If the user message is too long, we need to cut it off
        if len(self.encoder.encode(prompts.user)) > self.max_prompt_tokens:
            logger.warning(f"User prompt is too long. Cutting off to about {self.max_prompt_tokens} tokens.")
            # every token is about 2.5 characters
            prompts.user = (
                prompts.user[: int(round(self.max_prompt_tokens * 2.5) / 2)]
                + "[...CUTOFF DUE TO TOO LONG TEXT...]"
                + prompts.user[-int(round(self.max_prompt_tokens * 2.5) / 2) :]
            )

        if len(self.encoder.encode(prompts.sys)) > self.max_prompt_tokens:
            logger.warning(f"Sys prompt is too long. Cutting off to about {self.max_prompt_tokens} tokens.")
            # every token is about 2.5 characters
            prompts.sys = (
                prompts.sys[: int(round(self.max_prompt_tokens * 2.5) / 2)]
                + "[...CUTOFF DUE TO TOO LONG TEXT...]"
                + prompts.sys[-int(round(self.max_prompt_tokens * 2.5) / 2) :]
            )

        return prompts
