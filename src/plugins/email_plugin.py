"""
Email Plugin for TTBT5.
Provides email notification capabilities.
"""

def on_load(bot):
    """Called when the plugin is loaded."""
    bot.logger.info("Email plugin loaded")

def on_unload(bot):
    """Called when the plugin is unloaded."""
    bot.logger.info("Email plugin unloaded")

def on_start(bot):
    """Called when the bot starts."""
    bot.logger.info("Email plugin started")

def on_stop(bot):
    """Called when the bot stops."""
    bot.logger.info("Email plugin stopped")

def send_email(bot, recipient, subject, body):
    """Send an email notification."""
    bot.logger.info(f"Sending email to {recipient}: {subject}")
    # TODO: Implement actual email sending functionality
    return f"Email sent to {recipient}: {subject}"
