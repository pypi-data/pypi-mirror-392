# pitchai-gpt (`lib_agents`)

Reusable GPT helpers and the Fast Streaming Agent runtime that power AFASAsk deployments. The package bundles two major pieces of functionality:

- `lib_agents.gpt` / `lib_agents.gpt_root`: async GPT helpers with smart prompt loading, Gemini/OpenRouter/Groq/Azure routing, and streaming support.
- `lib_agents.fast_streaming_agent_root`: the Fast Streaming Agent runtime for dataframe-aware copilots, including dataframe loading, semantic-layer hooks, and templated UI helpers.

Both modules are designed to be shared between repositories (e.g. AFASAsk and AI Price Crawler) so they can evolve in one place and be installed through PyPI. The distribution on PyPI is called **`pitchai-gpt`**, but it exposes the `lib_agents` Python package to avoid breaking existing imports.

## Installation

```bash
uv pip install pitchai-gpt
# or
pip install pitchai-gpt
```

## Environment variables

The GPT helpers expect API keys/endpoints to be provided through environment variables (or by passing `api_key=` directly when instantiating `GPT`). The most commonly used variables are:

| Provider | Variables |
| --- | --- |
| Azure OpenAI | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_GPT4O_ENDPOINT`, `AZURE_OPENAI_GPT4O_MINI_ENDPOINT`, `AZURE_OPENAI_O3_ENDPOINT`, `AZURE_OPENAI_GPT5_MINI_ENDPOINT`, `AZURE_OPENAI_API_VERSION` |
| Gemini | `GEMINI_API_KEY_GENERAL` or `GEMINI_API_KEY`, optional `GEMINI_API_BASE_URL` |
| Groq | `GROQ_API_KEY` |
| OpenRouter | `OPENROUTER_API_KEY` |

The streaming agent runtime reads configuration from YAML/JSON prompt files, optionally loads `.env` files via `python-dotenv`, and integrates with Pandas/Polars. Make sure your application provides any referenced config modules (e.g. `configs.server_config`, `libs.lib_utils`).

## Usage

```python
from lib_agents.gpt.gpt import GPT

gpt = GPT(
    sys_msg="You are a concise assistant.",
    user_msg="Say READY",
    model="gemini-2.0-flash",
)
response, *_ = asyncio.run(gpt.run())
print(response)
```

For streaming agents see `lib_agents.fast_streaming_agent_root.main.FastStreamingAgent` and the demos under `apps/web_app`.

## Development

This project uses [Hatch](https://hatch.pypa.io) via `uv` for building and publishing. See `docs/uv_pypi_publish.md` in the monorepo for a step-by-step release checklist.
