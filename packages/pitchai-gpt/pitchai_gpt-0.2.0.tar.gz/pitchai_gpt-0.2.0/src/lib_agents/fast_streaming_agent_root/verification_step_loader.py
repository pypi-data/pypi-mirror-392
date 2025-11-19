"""Verification Step Loader Module.

Handles loading and injection of verification step from config.
Prompts the agent to triple-verify its findings after initial completion.
"""

import json
import importlib.util
from pathlib import Path
from typing import Any, Dict


class VerificationStepLoader:
    """Loads and manages verification step configuration from config."""
    
    def __init__(self, config_path: str | None = None, config_dict: Dict[str, Any] | None = None) -> None:
        """Initialize the verification step loader.
        
        Args:
            config_path: Path to config file with verification step configuration.
            config_dict: Config dictionary (used when already loaded from Python file).
        """
        self.enabled = False
        self.user_message_template = ""
        
        if config_dict:
            self._load_from_dict(config_dict)
        elif config_path and Path(config_path).exists():
            self._load_config(config_path)
    
    def _load_from_dict(self, config: Dict[str, Any]) -> None:
        """Load verification step configuration from dictionary.
        
        Args:
            config: Configuration dictionary.
        """
        verification_config = config.get("verification_step", {})
        self.enabled = verification_config.get("enabled", False)
        self.user_message_template = verification_config.get(
            "user_message_template", 
            "Please verify your answer is correct and complete."
        )
    
    def _load_config(self, config_path: str) -> None:
        """Load verification step configuration from file.
        
        Args:
            config_path: Path to config file (JSON or Python).
        """
        path = Path(config_path)
        
        if path.suffix == '.py':
            # Load Python config file
            spec = importlib.util.spec_from_file_location("config", config_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                config = getattr(module, "AGENT_CONFIG", {})
                self._load_from_dict(config)
        else:
            # Load JSON config file
            with open(config_path) as f:
                config = json.load(f)
                self._load_from_dict(config)
    
    def is_enabled(self) -> bool:
        """Check if verification step is enabled.
        
        Returns:
            True if enabled, False otherwise.
        """
        return self.enabled
    
    def get_verification_message(self) -> str | None:
        """Get the verification user message.
        
        Returns:
            Verification message string or None if not enabled.
        """
        if not self.enabled or not self.user_message_template:
            return None
        
        return self.user_message_template