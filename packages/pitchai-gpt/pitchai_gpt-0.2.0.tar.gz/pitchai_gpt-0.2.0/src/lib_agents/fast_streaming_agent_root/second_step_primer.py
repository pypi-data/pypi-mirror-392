"""Second Step Primer Module.

Handles loading and injection of second step reasoning primers from config.
Guides the agent to explore data thoroughly before main analysis.
"""

import json
import importlib.util
from pathlib import Path
from typing import Any, Dict


class SecondStepPrimer:
    """Loads and manages second step reasoning primers from config."""
    
    def __init__(self, config_path: str | None = None, config_dict: Dict[str, Any] | None = None) -> None:
        """Initialize the second step primer.
        
        Args:
            config_path: Path to config file with second step configuration.
            config_dict: Config dictionary (used when already loaded from Python file).
        """
        self.enabled = False
        self.reasoning_template = ""
        
        if config_dict:
            self._load_from_dict(config_dict)
        elif config_path and Path(config_path).exists():
            self._load_config(config_path)
    
    def _load_from_dict(self, config: Dict[str, Any]) -> None:
        """Load second step configuration from dictionary.
        
        Args:
            config: Configuration dictionary.
        """
        second_step_config = config.get("second_step", {})
        self.enabled = second_step_config.get("enabled", False)
        self.reasoning_template = second_step_config.get("reasoning_template", "")
    
    def _load_config(self, config_path: str) -> None:
        """Load second step configuration from file.
        
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
        """Check if second step primer is enabled.
        
        Returns:
            True if enabled, False otherwise.
        """
        return self.enabled
    
    def get_reasoning_primer(self) -> str | None:
        """Get the second step reasoning primer.
        
        Returns:
            Reasoning primer string or None if not enabled.
        """
        if not self.enabled or not self.reasoning_template:
            return None
        
        return self.reasoning_template