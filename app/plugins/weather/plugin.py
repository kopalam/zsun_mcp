"""Weather plugin implementation for FastMCP API service framework."""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Callable, Tuple
import httpx
from pydantic import BaseModel, Field

from plugins.base import BasePlugin

logger = logging.getLogger(__name__)


class WeatherRequest(BaseModel):
    """Pydantic model for weather request validation."""
    city: str = Field(..., description="City name to get weather for")


class WeatherPlugin(BasePlugin):
    """Weather plugin that provides weather information for cities."""

    def __init__(self):
        super().__init__("weather")
        self.weather_api_base = os.getenv("WEATHER_API_BASE", "https://api.openweathermap.org/data/2.5")
        self.weather_api_key = os.getenv("WEATHER_API_KEY", "cbca4319f933ed0c631bcd4ac7907f37")
        
        # HTTP client with proper headers
        self.http_client = httpx.AsyncClient(
            headers={
                "User-Agent": "FastMCP-Weather-Plugin/1.0",
                "Accept": "application/json"
            },
            timeout=30.0
        )

    def tools(self) -> List[Callable]:
        """Return the list of weather-related tools."""
        return [self.get_weather]

    async def get_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather information for a city.
        
        Args:
            city: Name of the city to get weather for.
            
        Returns:
            Dictionary containing weather information or error details.
        """
        try:
            # Validate input
            request = WeatherRequest(city=city)
            
            # Get weather data directly from OpenWeatherMap API
            weather_data = await self._get_weather_data(city)
            if weather_data is None:
                return self.jsonrpc_err(
                    -32603,  # INTERNAL_ERROR
                    f"Could not get weather data for city: {city}",
                    {"city": city, "error_type": "weather_api_failed"}
                )
            
            # Format response based on OpenWeatherMap API structure
            result = {
                "city": weather_data.get("name", city),
                "lat": weather_data.get("coord", {}).get("lat"),
                "lon": weather_data.get("coord", {}).get("lon"),
                "temperature_c": weather_data.get("main", {}).get("temp", 0),
                "feels_like": weather_data.get("main", {}).get("feels_like", 0),
                "humidity": weather_data.get("main", {}).get("humidity", 0),
                "pressure": weather_data.get("main", {}).get("pressure", 0),
                "windspeed": weather_data.get("wind", {}).get("speed", 0),
                "wind_direction": weather_data.get("wind", {}).get("deg", 0),
                "weather_main": weather_data.get("weather", [{}])[0].get("main", ""),
                "weather_description": weather_data.get("weather", [{}])[0].get("description", ""),
                "weather_icon": weather_data.get("weather", [{}])[0].get("icon", ""),
                "visibility": weather_data.get("visibility", 0),
                "clouds": weather_data.get("clouds", {}).get("all", 0),
                "country": weather_data.get("sys", {}).get("country", ""),
                "sunrise": weather_data.get("sys", {}).get("sunrise", 0),
                "sunset": weather_data.get("sys", {}).get("sunset", 0),
                "observed_at": datetime.fromtimestamp(weather_data.get("dt", 0)).isoformat(),
                "provider": "openweathermap"
            }
            
            logger.info(f"Weather data retrieved for {city}: {result['temperature_c']}°C")
            return self.jsonrpc_ok(result)
            
        except Exception as e:
            logger.error(f"Error getting weather for {city}: {str(e)}")
            return self.jsonrpc_err(
                -32603,  # INTERNAL_ERROR
                f"An error occurred while getting weather: {str(e)}",
                {"city": city, "error_type": "unknown_error", "detail": str(e)}
            )


    async def _get_weather_data(self, city: str) -> Dict[str, Any]:
        """Get weather data for given city using OpenWeatherMap API.
        
        Args:
            city: Name of the city.
            
        Returns:
            Dictionary containing weather data or None if failed.
        """
        try:
            # Use OpenWeatherMap API
            url = f"{self.weather_api_base}/weather"
            params = {
                "q": city,
                "appid": self.weather_api_key,
                "units": "metric",
                "lang": "zh_cn"
            }
            
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if the response indicates an error
            if data.get("cod") != 200:
                logger.warning(f"Weather API returned error for city {city}: {data.get('message', 'Unknown error')}")
                return None
            
            logger.info(f"Weather data retrieved for city: {city}")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during weather data fetch for {city}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during weather data fetch for {city}: {str(e)}")
            return None


    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
