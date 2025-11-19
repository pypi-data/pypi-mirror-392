import openai
import json
import asyncio
import os
from typing import Union, AsyncGenerator, List, Dict, Any, Callable, Awaitable, Optional
from .prompt_loader import Prompts
from rich import print
from .fallback_gpt_models import use_fall_back_on_fail
import tiktoken
import logging

import httpx


class CustomAsyncHTTPClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        kwargs.pop("proxies", None)  # Remove the 'proxies' argument if present
        super().__init__(*args, **kwargs)


async def _maybe_await(result: Any) -> None:
    if asyncio.iscoroutine(result):
        await result
    elif hasattr(result, "__await__"):
        await result


class StreamObserver:
    """Base class for observing streamed LLM text without blocking the stream."""

    async def on_text(self, text: str) -> None:
        """Handle a new chunk of text."""

    async def on_complete(self) -> None:
        """Called once the stream finishes."""


class PatternStreamObserver(StreamObserver):
    """Detects patterns in the stream and invokes a callback when matched."""

    def __init__(
        self,
        patterns: List[str],
        callback: Callable[[str, str], Awaitable[None] | None],
        *,
        once: bool = True,
        buffer_keep: int = 2000,
        case_sensitive: bool = False,
    ) -> None:
        self._case_sensitive = case_sensitive
        normalised = [p if case_sensitive else p.lower() for p in patterns]
        self._patterns = list(zip(normalised, patterns))
        self._callback = callback
        self._buffer = ""
        self._once = once
        self._triggered: set[str] = set()
        self._buffer_keep = buffer_keep

    def _normalise(self, text: str) -> str:
        return text if self._case_sensitive else text.lower()

    async def on_text(self, text: str) -> None:
        normalised = self._normalise(text)
        self._buffer += normalised
        self._buffer = self._buffer[-self._buffer_keep :]

        for normalised_pattern, original_pattern in self._patterns:
            if self._once and normalised_pattern in self._triggered:
                continue
            if normalised_pattern in self._buffer:
                await _maybe_await(self._callback(original_pattern, text))
                if self._once:
                    self._triggered.add(normalised_pattern)


class StreamInterceptWrapper:
    """Async iterator that forwards stream chunks and notifies observers."""

    def __init__(self, source_stream: AsyncGenerator, observers: List[StreamObserver]) -> None:
        self._source_iter = source_stream.__aiter__()
        self._observers = observers
        self._completed = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            chunk = await self._source_iter.__anext__()
        except StopAsyncIteration:
            if not self._completed:
                self._completed = True
                await asyncio.gather(*(observer.on_complete() for observer in self._observers))
            raise

        text = ""
        try:
            if chunk and len(chunk.choices) and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
        except AttributeError:
            text = getattr(chunk, "content", "")

        if text:
            await asyncio.gather(*(observer.on_text(text) for observer in self._observers))

        return chunk


# my_class.py

logger = logging.getLogger(__name__)
class GPT:
    """
    A utility class for interacting with OpenAI's GPT-based models, supporting direct user queries, tool invocation, and tool selection.

    This class allows for different modes of interaction with the GPT model:
    - Direct textual responses.
    - Function (tool) invocation with a specific schema.
    - Selection among multiple tools based on context.
    - Processing images along with text (multimodal capabilities).

    Attributes:
        client (openai.OpenAI): The OpenAI client used for API calls.
        msg_list (list[dict]): A list of messages formatted for the OpenAI API.
        function_call_schema (dict, optional): A specific schema for a function call.
        function_call_schema_list (list[dict], optional): A list of schemas for multiple function calls.
        model (str): The model to use, defaulting to "gpt-4o".

    Methods:
        construct_msg(sys_msg: str, user_msg: str) -> list[dict]:
            Constructs the message list from system and user messages.

        get_tool_response() -> dict:
            Executes a specific tool call based on the provided schema and returns the arguments.

        select_tool() -> tuple[str, dict]:
            Allows the model to select a tool from a list of schemas and returns the selected tool's name and arguments.

        get_response() -> str:
            Gets a streamed textual response from the model, printing it chunk by chunk.

        run() -> Union[str, tuple[str, dict], dict]:
            Determines the interaction mode (textual response, single tool, or tool selection) and executes accordingly.
    """

    def __init__(
        self,
        sys_msg: str = None,
        user_msg: str = None,
        function_call_schema: dict = None,
        function_call_schema_list: list[dict] = None,
        msg_list: list[dict] = None,
        stream: bool = False,
        model="gpt-4o",
        prompts: Prompts = None,
        api_key: str | None = None,
    ) -> None:
        self.prompts = None
        if prompts:
            self.prompts = prompts
            sys_msg = prompts.sys
            user_msg = prompts.user
            if prompts.parse_schema:
                function_call_schema = prompts.parse_schema

        self.msg_list = self.construct_msg_list(sys_msg, user_msg)

        self.fallback_mapping = {
            'gemini-2.0-flash': 'gemini-2.0-flash-lite',
            'gemini-2.0-flash-lite': 'gpt-4o-mini',
            'gemini-2.5-flash': 'gemini-2.5-flash-lite',
            'gemini-2.5-flash-lite': 'gpt-4o-mini',
            'gpt-4o': 'gpt-4o-mini'}

        # Overwrite the message list if it is explicitly given
        if msg_list:
            self.msg_list = msg_list

        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except Exception as e:
            self.encoder = tiktoken.encoding_for_model('gpt-4o')

        self.function_call_schema = function_call_schema
        self.function_call_schema_list = function_call_schema_list

        self.max_prompt_tokens = 64000

        self.model = model
        self.stream = stream
        self.api_key_override = api_key
        self.initialize_client()


    def initialize_client(self):
        azure_api_key = self.api_key_override or os.getenv("AZURE_OPENAI_API_KEY")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        def _require_azure_key() -> str:
            if not azure_api_key:
                raise RuntimeError("Set AZURE_OPENAI_API_KEY (or pass api_key) to use Azure-hosted OpenAI models.")
            return azure_api_key

        if self.model in ["gpt-4o", "gpt-4o-mini"]:
            endpoint = os.getenv("AZURE_OPENAI_GPT4O_ENDPOINT")
            if self.model == "gpt-4o-mini":
                endpoint = os.getenv("AZURE_OPENAI_GPT4O_MINI_ENDPOINT") or endpoint
            if not azure_api_key or not endpoint:
                raise RuntimeError("AZURE_OPENAI_API_KEY and GPT4O endpoint env vars must be set for Azure GPT models.")
            self.client = openai.AsyncAzureOpenAI(
                api_key=_require_azure_key(),
                azure_endpoint=endpoint,
                api_version=azure_api_version,
                 http_client=CustomAsyncHTTPClient(),
            )
        elif self.model in ["llama-3.3-70b-versatile", "llama-3.3-70b-specdec", "llama-3.1-8b-instant", "llama-3.1-70b-versatile", "llama3-8b-8192", "llama3-70b-8192"]:
            # Run with Groq for fast Llama models - check this first before OpenRouter
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise RuntimeError("Set GROQ_API_KEY to use Groq hosted Llama models.")
            self.client = openai.AsyncOpenAI(
                api_key=groq_api_key,
                base_url="https://api.groq.com/openai/v1",
                http_client=CustomAsyncHTTPClient(),
            )
        elif self.model in ["deepseek/deepseek-r1", "anthropic/claude-sonnet-4"]:
            # Run with OpenRouter for other models
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            if not openrouter_api_key:
                raise RuntimeError("Set OPENROUTER_API_KEY to use OpenRouter hosted models.")
            self.client = openai.AsyncOpenAI(
                api_key=openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                 http_client=CustomAsyncHTTPClient(),
            )
        elif self.model in ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash", "gemini-2.5-flash-lite"]:
            # Use staging's newer API key that doesn't have referrer restrictions
            gemini_api_key = (
                self.api_key_override
                or os.getenv("GEMINI_API_KEY_GENERAL")
                or os.getenv("GEMINI_API_KEY")
            )
            if not gemini_api_key:
                raise RuntimeError("Set GEMINI_API_KEY_GENERAL or GEMINI_API_KEY to use Gemini models.")
            self.client = openai.AsyncOpenAI(
                api_key=gemini_api_key,
                base_url=os.getenv("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
                http_client=CustomAsyncHTTPClient(),
            )
        elif self.model == "o3-mini":
            o3_endpoint = os.getenv("AZURE_OPENAI_O3_ENDPOINT")
            if not o3_endpoint:
                raise RuntimeError("Set AZURE_OPENAI_O3_ENDPOINT to use o3-mini.")
            self.client = openai.AsyncAzureOpenAI(
                api_key=_require_azure_key(),
                azure_endpoint=o3_endpoint,
                api_version="2024-08-01-preview",
                 http_client=CustomAsyncHTTPClient(),
            )
        elif self.model == "gpt-5-mini":
            gpt5_endpoint = os.getenv("AZURE_OPENAI_GPT5_MINI_ENDPOINT")
            if not gpt5_endpoint:
                raise RuntimeError("Set AZURE_OPENAI_GPT5_MINI_ENDPOINT to use gpt-5-mini.")
            self.client = openai.AsyncAzureOpenAI(
                api_key=_require_azure_key(),
                azure_endpoint=gpt5_endpoint,
                api_version="2024-12-01-preview",
                 http_client=CustomAsyncHTTPClient(),
            )
        else:
            raise RuntimeError(f"Model {self.model} is not configured. Set an appropriate endpoint/key or extend initialize_client().")

    def construct_msg_list(self, sys_msg: str, user_msg: str) -> list[dict]:
        """Given system message and user message string, constructs the messages list for OpenAI API"""
        sys = {"role": "system", "content": sys_msg}
        user = {"role": "user", "content": user_msg}
        return [sys, user]

    def construct_multimodal_msg_list(self, sys_msg: str, user_msg: str, images: List[Dict[str, Any]] = None) -> list[dict]:
        """Constructs a multimodal message list with both text and images"""
        sys = {"role": "system", "content": sys_msg}
        
        # If there are no images, return standard message list
        if not images:
            user = {"role": "user", "content": user_msg}
            return [sys, user]
        
        # Create content array for multimodal message
        content = [{"type": "text", "text": user_msg}]
        
        # Add images to content
        for image in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": image["url"],
                    "detail": image.get("detail", "auto")
                }
            })
        
        user = {"role": "user", "content": content}
        return [sys, user]

    @use_fall_back_on_fail
    async def get_tool_response(self, func_call_schema: dict = None, msg_list: List[dict] = None) -> dict:
        """Executes a specific tool call based on the provided schema and returns the arguments."""
        if not func_call_schema:
            func_call_schema = self.function_call_schema

        if not msg_list:
            msg_list = self.msg_list

        response = await self.client.chat.completions.create(
            model='gemini-2.0-flash-lite', # Ugly hack, current provider might be openai while we try to use gemin, however, now all parsing will be much fater which previously was very slow
            messages=msg_list,
            stream=self.stream,
            tools=[func_call_schema],
            tool_choice=func_call_schema,
        )

        tool_call = response.choices[0].message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        return response, tool_name, tool_args

    @use_fall_back_on_fail
    async def select_tool(self) -> dict:
        """
        Allows the model to select a tool from a list of schemas and returns the selected tool's name and arguments.

        Returns:
            tuple[str, dict]: The name of the selected tool and its arguments.
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.msg_list,
            stream=self.stream,
            tools=self.function_call_schema_list,
        )

        try:
            tool_call = response.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            return response, function_name, tool_args
        except Exception as e:
            print('tool selection error')
            print(e)
            return None, None

    @use_fall_back_on_fail
    async def get_text_response(
        self,
        return_raw_stream: bool = False,
        silent: bool = True,
        msg_list: List[dict] = None,
        stream_observers: Optional[List["StreamObserver"]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    ) -> Union[str, AsyncGenerator]:
        """
        Gets a streamed textual response from the model, printing it chunk by chunk.

        Returns:
            str: The full response text.
            AsyncGenerator: The raw response stream. (if return_raw_stream=True)
        """
        if not msg_list:
            msg_list = self.msg_list

        request_kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": msg_list,
            "stream": True,
        }
        if tools:
            request_kwargs["tools"] = tools
        if tool_choice:
            request_kwargs["tool_choice"] = tool_choice

        response = await self.client.chat.completions.create(**request_kwargs)

        if return_raw_stream:
            if stream_observers:
                return StreamInterceptWrapper(response, stream_observers)
            return response

        # Print the chunks of the response and add them to the full message
        full_msg = ''

        async for chunk in response:
            if len(chunk.choices) == 0: continue
            if chunk and chunk.choices[0].delta.content:
                if not silent:
                    print(chunk.choices[0].delta.content, end="", flush=True)
                full_msg += chunk.choices[0].delta.content
                if stream_observers:
                    await asyncio.gather(
                        *(
                            observer.on_text(chunk.choices[0].delta.content)
                            for observer in stream_observers
                        )
                    )

        # Add the response to the message list
        self.msg_list.append(
            {"role": "assistant", "content": full_msg}
        )
        if stream_observers:
            await asyncio.gather(*(observer.on_complete() for observer in stream_observers))

        return full_msg


    async def run(self, silent=True, return_raw_stream=False, sys_msg: str = None, user_msg: str = None, function_call_schema: dict = None, prompts: Prompts = None):
        """
        Determines the interaction mode (textual response, single tool, or tool selection) and executes accordingly.

        Returns:
            Always returns a tuple of length 3, (response, tool_name, tool_args)
            But the tool_name and tool_args might be empty.
        """
        if prompts:
            # We want to trim the prompts very close to the actual LLM call itself
            prompts = await self.trim_prompts(prompts)
        else:
            prompts = await self.trim_prompts(self.prompts)
        

        if self.function_call_schema_list:
            return await self.select_tool()
        else:
            # Check if we have images to process
            has_images = prompts and hasattr(prompts, "images") and prompts.images
            
            if has_images:
                # Use multimodal message construction for images
                msg_list = self.construct_multimodal_msg_list(prompts.sys, prompts.user, prompts.images)
            else:
                # Use standard message construction
                msg_list = self.construct_msg_list(prompts.sys, prompts.user)
                
            # Parse if parsing prompts are present
            if prompts and prompts.parse_sys and prompts.parse_user:
                
                response = await self.get_text_response(silent=silent, return_raw_stream=False, msg_list=msg_list) # must be false here, otherwise we can't parse from it
                if not getattr(prompts, "skip_sys", False):
                    prompts.parse_sys = prompts.parse_sys.format(previous_response=response)
                prompts.parse_user = prompts.parse_user.format(previous_response=response)
                parse_msg_list = self.construct_msg_list(prompts.parse_sys, prompts.parse_user)
                tool_response, tool_name, tool_arg =  await self.get_tool_response(msg_list=parse_msg_list, func_call_schema=prompts.parse_schema)

                return response, tool_name, tool_arg
            else:

                response = await self.get_text_response(silent=silent, return_raw_stream=return_raw_stream, msg_list=msg_list)
                return response, None, None
            
            


    
    async def trim_prompts(self, prompts):
                # If the user message is too long, we need to cut it off
        if len(self.encoder.encode(prompts.user)) > self.max_prompt_tokens:
            logger.warning(
                f"User prompt is too long. Cutting off to about {self.max_prompt_tokens} tokens."
            )
            #every token is about 2.5 characters 
            prompts.user = prompts.user[:int(round(self.max_prompt_tokens*2.5)/2)] + "[...CUTOFF DUE TO TOO LONG TEXT...]" + prompts.user[-int(round(self.max_prompt_tokens*2.5)/2):]
        
        if len(self.encoder.encode(prompts.sys)) > self.max_prompt_tokens:
            logger.warning(
                f"Sys prompt is too long. Cutting off to about {self.max_prompt_tokens} tokens."
            )
            #every token is about 2.5 characters 
            prompts.sys = prompts.sys[:int(round(self.max_prompt_tokens*2.5)/2)] + "[...CUTOFF DUE TO TOO LONG TEXT...]" + prompts.sys[-int(round(self.max_prompt_tokens*2.5)/2):]

        return prompts
