"""Pre-Action Loader Module.

Handles loading and execution of pre-configured actions from config files.
Allows "faking" the first step with templated code blocks.
"""

import json
import importlib.util
from pathlib import Path
from typing import Any, Dict


class PreActionLoader:
    """Loads and manages pre-configured actions from config files."""
    
    def __init__(self, config_path: str | None = None, config_dict: Dict[str, Any] | None = None) -> None:
        """Initialize the pre-action loader.
        
        Args:
            config_path: Path to config file with pre-actions.
            config_dict: Config dictionary (used when already loaded from Python file).
        """
        self.enabled = False
        self.template = ""
        
        if config_dict:
            self._load_from_dict(config_dict)
        elif config_path and Path(config_path).exists():
            self._load_config(config_path)
    
    def _load_from_dict(self, config: Dict[str, Any]) -> None:
        """Load pre-action configuration from dictionary.
        
        Args:
            config: Configuration dictionary.
        """
        if "first_step" in config:
            self.enabled = config["first_step"].get("enabled", False)
            self.template = config["first_step"].get("template", "")
        else:
            # Backward compatibility with old field names
            self.enabled = config.get("enabled", False)
            self.template = config.get("template", "")
    
    def _load_config(self, config_path: str) -> None:
        """Load pre-action configuration from file.
        
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
        """Check if pre-action is enabled.
        
        Returns:
            True if enabled, False otherwise.
        """
        return self.enabled
    
    def format_pre_action(self, user_query: str) -> str | None:
        """Format the pre-action template with user query.
        
        Args:
            user_query: The user's query to use for template replacement.
            
        Returns:
            Formatted template string or None if not enabled.
        """
        if not self.enabled or not self.template:
            return None
        
        # Extract first significant word from user query for search term
        # (you could make this smarter with NLP if needed)
        words = user_query.lower().split()
        search_term = words[0] if words else ""
        
        # Replace template variables
        formatted = self.template.replace("{user_query}", user_query)
        formatted = formatted.replace("{search_term}", search_term)
        
        return formatted