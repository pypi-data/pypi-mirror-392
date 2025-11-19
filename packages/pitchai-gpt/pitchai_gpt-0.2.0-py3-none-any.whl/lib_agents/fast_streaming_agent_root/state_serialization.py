"""Serialization helpers for persisting FastStreamingAgent state."""

from __future__ import annotations

import asyncio
import os
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

import dill
from botocore.exceptions import ClientError

from lib_utils.storage.wasabi import WasabiConfigurationError, WasabiStorage

from .colors import Colors

if TYPE_CHECKING:
    from .main import FastStreamingAgent


_SERIALIZATION_TMP_ATTRS = (
    "shared_ui_msg",
    "templates",
    "standard_pseudo_request",
)


def remove_unpicklable_items(execution_globals: dict[str, Any]) -> None:
    """Strip asyncio primitives from *execution_globals* so dill can serialize."""

    unpicklable_keys: list[str] = []
    for key, value in execution_globals.items():
        if isinstance(value, (asyncio.Task, asyncio.Future)):
            unpicklable_keys.append(key)

    for key in unpicklable_keys:
        execution_globals.pop(key)
        print(f"🗑️  Removed unpicklable '{key}' from execution_globals")


@contextmanager
def _temporary_attribute_nullification(agent: "FastStreamingAgent") -> Any:
    """Temporarily set selected attributes to ``None`` during serialization."""

    original_values: dict[str, Any] = {}
    for attribute in _SERIALIZATION_TMP_ATTRS:
        if hasattr(agent, attribute):
            original_values[attribute] = getattr(agent, attribute)
            setattr(agent, attribute, None)

    try:
        yield
    finally:
        for attribute, value in original_values.items():
            setattr(agent, attribute, value)


def serialize_agent(agent: "FastStreamingAgent") -> bytes:
    """Return a serialized representation of *agent* using dill."""

    if agent is None:
        raise ValueError("Agent instance is required for serialization")

    remove_unpicklable_items(getattr(agent, "execution_globals", {}))

    with _temporary_attribute_nullification(agent):
        return dill.dumps(agent)


def deserialize_agent(payload: bytes) -> "FastStreamingAgent":
    """Reconstruct a :class:`FastStreamingAgent` instance from *payload*."""

    agent = dill.loads(payload)

    if hasattr(agent, "execution_runtime"):
        try:
            agent.execution_runtime.refresh_protected_names()  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover - defensive refresh
            pass

    for attribute in _SERIALIZATION_TMP_ATTRS:
        setattr(agent, attribute, None)

    return agent


async def save_agent_state(agent: "FastStreamingAgent", *, directory: Path | None = None) -> None:
    """Serialize *agent* to disk so a conversation can resume later."""

    conversation_id = getattr(agent, "conversation_id", None)
    if not conversation_id:
        return

    agents_dir = directory or Path("data/agents")
    agents_dir.mkdir(parents=True, exist_ok=True)

    agent_file = agents_dir / f"{conversation_id}.dill"
    print(f"{Colors.GREEN}[Serializing agent to {agent_file}]{Colors.RESET}")

    try:
        payload = serialize_agent(agent)
        agent_file.write_bytes(payload)

        file_size = agent_file.stat().st_size / 1024  # KB
        print(f"{Colors.GREEN}✓ Agent serialized ({file_size:.1f} KB){Colors.RESET}")
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"{Colors.RED}Error serializing agent: {exc}{Colors.RESET}")
        import traceback

        traceback.print_exc()


def _wasabi_key(conversation_id: str, chatconfig_id: str | None) -> str:
    prefix = os.environ.get("WASABI_AGENT_STATE_PREFIX", "agent-states")
    if chatconfig_id:
        prefix = f"{prefix}/{chatconfig_id}"
    return f"{prefix}/{conversation_id}.dill"


async def save_agent_state_to_wasabi(agent: "FastStreamingAgent") -> bool:
    """Persist the serialized agent to Wasabi object storage."""

    conversation_id = getattr(agent, "conversation_id", None)
    if not conversation_id:
        return False

    try:
        storage = WasabiStorage()
    except WasabiConfigurationError:
        return False

    chatconfig_id = getattr(agent, "chatconfig_id", None)
    key = _wasabi_key(conversation_id, chatconfig_id)
    payload = serialize_agent(agent)

    try:
        await asyncio.to_thread(storage.upload_bytes, key, payload)
        print(f"{Colors.GREEN}✓ Agent state uploaded to Wasabi at {key}{Colors.RESET}")
        return True
    except ClientError as exc:  # pragma: no cover - network failure
        print(f"{Colors.RED}Failed to upload agent state to Wasabi: {exc}{Colors.RESET}")
    except Exception as exc:  # pragma: no cover - defensive
        print(f"{Colors.RED}Unexpected error uploading agent state: {exc}{Colors.RESET}")

    return False


async def load_agent_state_from_wasabi(
    conversation_id: str,
    chatconfig_id: str | None,
) -> "FastStreamingAgent | None":
    """Load a serialized agent for *conversation_id* from Wasabi if available."""

    if not conversation_id:
        return None

    try:
        storage = WasabiStorage()
    except WasabiConfigurationError:
        return None

    key = _wasabi_key(conversation_id, chatconfig_id)

    try:
        payload = await asyncio.to_thread(storage.download_bytes, key)
        if payload is None:
            return None

        agent = deserialize_agent(payload)
        setattr(agent, "conversation_id", conversation_id)
        setattr(agent, "chatconfig_id", chatconfig_id)
        return agent
    except ClientError as exc:
        error_code = getattr(exc, "response", {}).get("Error", {}).get("Code")
        if error_code not in {"404", "NoSuchKey", "NoSuchBucket"}:  # pragma: no cover - defensive
            print(f"{Colors.RED}Failed to download agent state from Wasabi: {exc}{Colors.RESET}")
        return None
    except FileNotFoundError:
        return None
    except Exception as exc:  # pragma: no cover - defensive
        print(f"{Colors.RED}Unexpected error loading agent state: {exc}{Colors.RESET}")
        return None


async def delete_agent_state_from_wasabi(
    conversation_id: str,
    chatconfig_id: str | None,
) -> bool:
    """Delete a stored agent state from Wasabi. Useful for tests and maintenance."""

    try:
        storage = WasabiStorage()
    except WasabiConfigurationError:
        return False

    key = _wasabi_key(conversation_id, chatconfig_id)

    try:
        await asyncio.to_thread(storage.delete_object, key)
        return True
    except ClientError as exc:  # pragma: no cover - defensive
        print(f"{Colors.RED}Failed to delete agent state from Wasabi: {exc}{Colors.RESET}")
        return False
