"""Time plugin for FastMCP API service framework."""

from .plugin import TimePlugin

# Create and export the time plugin instance
time_plugin = TimePlugin()

__all__ = ["TimePlugin", "time_plugin"]
