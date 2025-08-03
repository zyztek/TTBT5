#!/usr/bin/env python3
"""
Configuration module for the TTBT5 Application.
This module handles application configuration settings.
"""

import os
import json
from typing import Any, Dict, Optional

class Config:
    """Configuration class for the TTBT5 Application."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the configuration."""
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config file: {e}")
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration settings."""
        return {
            "app_name": "TTBT5",
            "version": "1.0.0",
            "debug": False,
            "log_level": "INFO",
            "features": ["core"]
        }
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config[key] = value
        self.save_config()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        self.config.update(updates)
        self.save_config()

# Global config instance
_app_config: Optional[Config] = None

def get_config() -> Config:
    """Get the application configuration instance."""
    global _app_config
    if _app_config is None:
        _app_config = Config()
    return _app_config
