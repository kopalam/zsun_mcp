"""Plugins package for FastMCP API service framework."""

from .weather import weather_plugin
from .time import time_plugin

__all__ = ["weather_plugin", "time_plugin"]
