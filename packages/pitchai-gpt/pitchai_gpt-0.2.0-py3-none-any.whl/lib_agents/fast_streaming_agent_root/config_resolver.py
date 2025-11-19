"""
Agent Configuration Resolver

This module provides functionality to resolve agent configuration paths
based on ChatConfig settings with fallback chains for multi-tenant support.
"""

import os
import logging
from pathlib import Path
from typing import Optional

try:
    from apps.web_app.src.web_app.chat.chatconfig import get_chat_config
except ModuleNotFoundError:  # pragma: no cover - CLI usage without web app
    get_chat_config = None  # type: ignore[assignment]

from fastapi import Request

logger = logging.getLogger(__name__)

# Mapping of chatconfig IDs to the underlying configuration folder
# Maintain aliases so legacy IDs (e.g. ortho_ridderkerk) reuse the same agent config
CONFIG_ALIASES = {
    "ortho_ridderkerk": "orthodontie_ridderkerk",
    "walburg": "ortho_walburg",
    "gzb_new": "gzb_new_test",
    "gzb_new_test_pandas": "gzb",
}


async def resolve_agent_config_path(request: Request = None, chatconfig_id: str = None) -> str:
    """
    Resolve the agent configuration path for a given chat config with fallback chain.
    
    Args:
        request: FastAPI request object (optional, used to get chatconfig_id from session)
        chatconfig_id: Explicit chat config ID (optional, overrides request session)
    
    Returns:
        str: Path to the agent configuration file
        
    Config resolution:
    1. ChatConfig.agent_config_path (if exists and file exists)
    2. configs/{chatconfig_id}/agent_config.yaml
    """
    
    # Determine chatconfig_id
    if not chatconfig_id:
        if request and hasattr(request, 'session'):
            chatconfig_id = request.session.get("CHATCONFIG_ID", "gzb")
        else:
            chatconfig_id = "gzb"
    
    logger.info(f"[CONFIG RESOLVER] Resolving agent config for chatconfig_id: {chatconfig_id}")
    lookup_id = CONFIG_ALIASES.get(chatconfig_id, chatconfig_id)
    if lookup_id != chatconfig_id:
        logger.info(f"[CONFIG RESOLVER] Using alias '{lookup_id}' for chatconfig '{chatconfig_id}'")
    
    # Get the project root directory
    project_root = Path(__file__).resolve().parents[5]
    
    try:
        # 1. Try to get agent_config_path from ChatConfig database
        if get_chat_config is not None:
            chat_config, _ = await get_chat_config(request, chatconfig_id)
            if chat_config and chat_config.agent_config_path:
                config_path = project_root / chat_config.agent_config_path
                if config_path.exists():
                    logger.info(f"[CONFIG RESOLVER] Using database-configured path: {config_path}")
                    return str(config_path)
                logger.warning(f"[CONFIG RESOLVER] Database path not found: {config_path}")
    
    except Exception as e:
        logger.warning(f"[CONFIG RESOLVER] Failed to load chat config: {e}")
    
    # 2. Use organization-specific config path (YAML only)
    org_config_yaml_path = project_root / f"configs/{lookup_id}/agent_config.yaml"
    if org_config_yaml_path.exists():
        logger.info(f"[CONFIG RESOLVER] Using organization YAML config: {org_config_yaml_path}")
        return str(org_config_yaml_path)

    org_config_json_path = project_root / f"configs/{lookup_id}/agent_config.json"
    if org_config_json_path.exists():
        logger.info(f"[CONFIG RESOLVER] Using organization JSON config: {org_config_json_path}")
        return str(org_config_json_path)
    
    # If no config found, raise an error
    logger.error(f"[CONFIG RESOLVER] No agent config found at: {org_config_yaml_path} or {org_config_json_path}")
    raise FileNotFoundError(f"Agent configuration file not found: {org_config_yaml_path} or {org_config_json_path}")


def resolve_agent_config_path_sync(chatconfig_id: str = "gzb") -> str:
    """
    Synchronous version of resolve_agent_config_path for standalone usage.
    
    Args:
        chatconfig_id: Chat config ID to resolve for
    
    Returns:
        str: Path to the agent configuration file
        
    Note: This version only uses YAML file-based configs since it can't access the database
    """
    
    logger.info(f"[CONFIG RESOLVER SYNC] Resolving agent config for chatconfig_id: {chatconfig_id}")
    lookup_id = CONFIG_ALIASES.get(chatconfig_id, chatconfig_id)
    if lookup_id != chatconfig_id:
        logger.info(f"[CONFIG RESOLVER SYNC] Using alias '{lookup_id}' for chatconfig '{chatconfig_id}'")
    
    # Get the project root directory
    project_root = Path(__file__).resolve().parents[5]
    
    # 1. Use organization-specific config path (YAML only)
    org_config_yaml_path = project_root / f"configs/{lookup_id}/agent_config.yaml"
    if org_config_yaml_path.exists():
        logger.info(f"[CONFIG RESOLVER SYNC] Using organization YAML config: {org_config_yaml_path}")
        return str(org_config_yaml_path)

    org_config_json_path = project_root / f"configs/{lookup_id}/agent_config.json"
    if org_config_json_path.exists():
        logger.info(f"[CONFIG RESOLVER SYNC] Using organization JSON config: {org_config_json_path}")
        return str(org_config_json_path)
    
    # If no config found, raise an error
    logger.error(f"[CONFIG RESOLVER SYNC] No agent config found at: {org_config_yaml_path} or {org_config_json_path}")
    raise FileNotFoundError(f"Agent configuration file not found: {org_config_yaml_path} or {org_config_json_path}")
