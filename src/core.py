#!/usr/bin/env python3
"""
Core module for the TTBT5 Application.
This module contains the main application logic.
"""

import os
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from src.config import get_config
from src.logger import get_logger
from src.commands import CommandProcessor
from src.plugin_manager import PluginManager
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ApplicationState:
    """Represents the application state."""
    start_time: datetime
    version: str = "1.0.0"
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        self.features.append("core")

class TTBT5App:
    """Main application class."""
    
    def __init__(self):
        # Initialize logger
        self.logger = get_logger()
        self.logger.info("Initializing TTBT5 Application")
        
        # Initialize config
        self.config = get_config()
        self.logger.info("Configuration loaded")
        
        # Initialize command processor
        self.command_processor = CommandProcessor(self.logger)
        self.register_commands()
        
        # Initialize plugin manager
        self.plugin_manager = PluginManager()
        self.logger.info("Plugin manager initialized")
        
        # Initialize state
        self.state = ApplicationState(
            start_time=datetime.now(),
            version=self.config.get("version", "1.0.0")
        )
        
        self.logger.info("TTBT5 Application initialized successfully")
    
    def register_commands(self):
        """Register available commands."""
        self.command_processor.register_command("status", self.get_status)
        self.command_processor.register_command("help", self.show_help, ["h", "?"])
        self.command_processor.register_command("config", self.show_config)
        self.command_processor.register_command("info", self.get_info)
        self.command_processor.register_command("load_plugin", self.load_plugin)
        self.command_processor.register_command("exec_hook", self.execute_hook)
    
    def get_status(self) -> Dict:
        """Get the current application status."""
        return {
            "status": "running",
            "version": self.state.version,
            "start_time": self.state.start_time.isoformat(),
            "features": self.state.features
        }
    
    def show_help(self):
        """Show help information."""
        help_text = """
TTBT5 Application Help
======================

Available commands:
- status: Show application status
- help: Show this help message
- config: Show current configuration
- load_plugin <path>: Load a plugin from the specified file path
- exec_hook <hook_name> [args...]: Execute a plugin hook by name with optional arguments

For more information, please refer to the documentation.
        """
        print(help_text)
        return help_text
    
    def show_config(self):
        """Show current configuration."""
        config_data = self.config.config
        print("Current Configuration:")
        for key, value in config_data.items():
            print(f"  {key}: {value}")
        return config_data
    
    def get_info(self) -> Dict:
        """Get detailed application information."""
        info = {
            "name": self.config.get("app_name"),
            "version": self.config.get("version"),
            "features": self.state.features,
            "start_time": self.state.start_time.isoformat(),
            "status": "running"
        }
        print("Application Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        return info
    
    def load_plugin(self, plugin_path: str):
        """Load a plugin from the given file path."""
        self.logger.info(f"Loading plugin from {plugin_path}")
        self.plugin_manager.load_plugin(plugin_path)
        self.logger.info(f"Plugin loaded from {plugin_path}")
        return f"Plugin loaded from {plugin_path}"
    
    def execute_hook(self, hook_name: str, *args):
        """Execute a plugin hook by name with optional arguments."""
        self.logger.info(f"Executing hook {hook_name} with args {args}")
        result = self.plugin_manager.execute_hook(hook_name, *args)
        self.logger.info(f"Hook {hook_name} executed with result: {result}")
        return result
    
    def run_command(self, command: str, *args, **kwargs):
        """Run a command."""
        try:
            self.logger.info(f"Executing command: {command}")
            result = self.command_processor.execute_command(command, *args, **kwargs)
            self.logger.info(f"Command {command} executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error executing command {command}: {e}")
            raise

if __name__ == "__main__":
    app = TTBT5App()
    print("TTBT5 Application")
    print("Status:", "Running" if True else "Stopped")
    print("Please provide the TTBT2 requirements to implement the full application")
    print("Available commands: status, help, config, load_plugin, exec_hook")
