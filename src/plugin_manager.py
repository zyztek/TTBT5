"""
Plugin Manager for TTBT5.
Handles loading and executing plugins.
"""

import os
import sys
import importlib.util
from typing import Any, Callable, Dict, List, Optional

class PluginManager:
    """Manages plugins for the TTBT5 application."""
    
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.hooks: Dict[str, List[tuple]] = {}
    
    def load_plugin(self, plugin_path: str) -> None:
        """Load a plugin from the given file path."""
        if not os.path.exists(plugin_path):
            raise FileNotFoundError(f"Plugin file not found: {plugin_path}")
        
        # Get the plugin name from the file name
        plugin_name = os.path.splitext(os.path.basename(plugin_path))[0]
        
        # Load the plugin module
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        if spec is None:
            raise ImportError(f"Could not load plugin spec from {plugin_path}")
        module = importlib.util.module_from_spec(spec)
        if spec.loader is not None:
            spec.loader.exec_module(module)
        
        # Store the plugin
        self.plugins[plugin_name] = module
        
        # Register hooks
        if hasattr(module, 'on_load'):
            self.hooks.setdefault('on_load', []).append((plugin_name, module.on_load))
        if hasattr(module, 'on_unload'):
            self.hooks.setdefault('on_unload', []).append((plugin_name, module.on_unload))
        if hasattr(module, 'on_start'):
            self.hooks.setdefault('on_start', []).append((plugin_name, module.on_start))
        if hasattr(module, 'on_stop'):
            self.hooks.setdefault('on_stop', []).append((plugin_name, module.on_stop))
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute a plugin hook by name with optional arguments."""
        results: List[Any] = []
        if hook_name in self.hooks:
            for plugin_name, hook_func in self.hooks[hook_name]:
                try:
                    # For demonstration, we'll pass a mock bot instance
                    # In a real implementation, this would be the actual bot instance
                    mock_bot = type('MockBot', (), {'logger': type('MockLogger', (), {'info': lambda self, msg: print(f"[{plugin_name}] {msg}")})()})
                    result = hook_func(mock_bot, *args, **kwargs)
                    results.append(result)
                except Exception as e:
                    print(f"Error executing hook {hook_name} in plugin {plugin_name}: {e}")
        return results
    
    def unload_plugin(self, plugin_name: str) -> None:
        """Unload a plugin by name."""
        if plugin_name in self.plugins:
            module = self.plugins[plugin_name]
            if hasattr(module, 'on_unload'):
                try:
                    mock_bot = type('MockBot', (), {'logger': type('MockLogger', (), {'info': lambda self, msg: print(f"[{plugin_name}] {msg}")})()})
                    module.on_unload(mock_bot)
                except Exception as e:
                    print(f"Error unloading plugin {plugin_name}: {e}")
            
            # Remove hooks for this plugin
            for hook_list in self.hooks.values():
                hook_list[:] = [item for item in hook_list if item[0] != plugin_name]
            
            # Remove the plugin
            del self.plugins[plugin_name]
    
    def get_loaded_plugins(self) -> List[str]:
        """Get a list of loaded plugin names."""
        return list(self.plugins.keys())
