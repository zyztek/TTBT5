#!/usr/bin/env python3
"""
Command module for the TTBT5 Application.
This module handles command processing for the application.
"""

from typing import Dict, Callable, List
from src.config import get_config
from src.logger import Logger

class CommandProcessor:
    """Process commands for the TTBT5 Application."""
    
    def __init__(self, logger: Logger):
        """Initialize the command processor."""
        self.logger = logger
        self.commands = {}
        self.aliases = {}
    
    def register_command(self, name: str, func: Callable, alias: List[str] = None):
        """Register a command."""
        self.commands[name] = func
        if alias:
            for a in alias:
                self.aliases[a] = name
    
    def execute_command(self, command: str, *args, **kwargs):
        """Execute a command."""
        # Check if it's an alias
        if command in self.aliases:
            command = self.aliases[command]
        
        if command in self.commands:
            try:
                return self.commands[command](*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error executing command {command}: {e}")
                raise
        else:
            self.logger.error(f"Unknown command: {command}")
            raise ValueError(f"Unknown command: {command}")

# Example usage
if __name__ == "__main__":
    # This is just for testing the command processor
    pass
