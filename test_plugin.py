"""
Test plugin for TTBT5.
"""

def on_load(bot):
    """Called when the plugin is loaded."""
    bot.logger.info("Test plugin loaded successfully!")
    return "Test plugin loaded"

def on_unload(bot):
    """Called when the plugin is unloaded."""
    bot.logger.info("Test plugin unloaded successfully!")
    return "Test plugin unloaded"

def on_start(bot):
    """Called when the application starts."""
    bot.logger.info("Test plugin: Application started!")
    return "Application started"

def on_stop(bot):
    """Called when the application stops."""
    bot.logger.info("Test plugin: Application stopped!")
    return "Application stopped"

def test_command(bot, *args):
    """A test command."""
    bot.logger.info(f"Test command executed with args: {args}")
    return f"Test command executed with {len(args)} arguments"
