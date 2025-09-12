"""Weather plugin for FastMCP API service framework."""

from .plugin import WeatherPlugin

# Create and export the weather plugin instance
weather_plugin = WeatherPlugin()

__all__ = ["WeatherPlugin", "weather_plugin"]
