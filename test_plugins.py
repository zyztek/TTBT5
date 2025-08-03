#!/usr/bin/env python3
"""
Test script for plugin functionality.
"""

import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.plugin_manager import PluginManager

def test_plugin_manager():
    """Test the PluginManager functionality."""
    print("Testing PluginManager...")
    
    # Create a plugin manager
    plugin_manager = PluginManager()
    
    # Load a plugin
    plugin_path = os.path.join(os.path.dirname(__file__), 'src', 'plugins', 'telegram_plugin.py')
    print(f"Loading plugin from: {plugin_path}")
    
    try:
        plugin_manager.load_plugin(plugin_path)
        print("Plugin loaded successfully!")
    except Exception as e:
        print(f"Error loading plugin: {e}")
        return
    
    # Check loaded plugins
    loaded_plugins = plugin_manager.get_loaded_plugins()
    print(f"Loaded plugins: {loaded_plugins}")
    
    # Execute a hook
    print("Executing on_load hook...")
    results = plugin_manager.execute_hook('on_load')
    print(f"Hook execution results: {results}")
    
    # Test plugin-specific function
    print("Testing plugin-specific function...")
    # This would normally be done through the bot instance
    # For now, we'll just verify the plugin is loaded
    
    print("Plugin test completed!")

if __name__ == "__main__":
    test_plugin_manager()
