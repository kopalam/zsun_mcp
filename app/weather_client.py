"""Weather client example for FastMCP API service framework."""

import asyncio
import json
import logging
import sys
from typing import Any, Dict

from fastmcp import FastMCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeatherClient:
    """Client for interacting with the FastMCP Weather API."""

    def __init__(self, server_url: str = "http://localhost:8010/sse"):
        """Initialize the weather client.
        
        Args:
            server_url: URL of the FastMCP server SSE endpoint.
        """
        self.server_url = server_url
        self.client = None

    async def connect(self):
        """Connect to the FastMCP server."""
        try:
            self.client = FastMCPClient(self.server_url)
            await self.client.connect()
            logger.info(f"Connected to FastMCP server at {self.server_url}")
        except Exception as e:
            logger.error(f"Failed to connect to server: {str(e)}")
            raise

    async def disconnect(self):
        """Disconnect from the FastMCP server."""
        if self.client:
            try:
                await self.client.disconnect()
                logger.info("Disconnected from FastMCP server")
            except Exception as e:
                logger.error(f"Error disconnecting from server: {str(e)}")

    async def get_weather(self, city: str) -> Dict[str, Any]:
        """Get weather information for a city.
        
        Args:
            city: Name of the city to get weather for.
            
        Returns:
            Dictionary containing weather information or error details.
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            logger.info(f"Requesting weather for city: {city}")
            
            # Call the get_weather tool
            result = await self.client.call_tool(
                name="get_weather",
                arguments={"city": city}
            )
            
            logger.info(f"Weather request completed for {city}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting weather for {city}: {str(e)}")
            return {
                "status": "error",
                "error": {
                    "code": "CLIENT_ERROR",
                    "message": str(e)
                }
            }

    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from the server.
        
        Returns:
            Dictionary containing available tools.
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            tools = await self.client.list_tools()
            logger.info(f"Retrieved {len(tools)} tools from server")
            return tools
        except Exception as e:
            logger.error(f"Error listing tools: {str(e)}")
            return {"error": str(e)}

    async def list_resources(self) -> Dict[str, Any]:
        """List available resources from the server.
        
        Returns:
            Dictionary containing available resources.
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            resources = await self.client.list_resources()
            logger.info(f"Retrieved {len(resources)} resources from server")
            return resources
        except Exception as e:
            logger.error(f"Error listing resources: {str(e)}")
            return {"error": str(e)}


async def demo_weather_client():
    """Demonstrate the weather client functionality."""
    client = WeatherClient()
    
    try:
        # Connect to the server
        print("Connecting to FastMCP server...")
        await client.connect()
        
        # List available tools
        print("\nListing available tools...")
        tools = await client.list_tools()
        print(f"Available tools: {json.dumps(tools, indent=2)}")
        
        # List available resources
        print("\nListing available resources...")
        resources = await client.list_resources()
        print(f"Available resources: {json.dumps(resources, indent=2)}")
        
        # Test weather requests
        test_cities = ["beijing", "london", "tokyo", "new york"]
        
        for city in test_cities:
            print(f"\n{'='*50}")
            print(f"Getting weather for: {city}")
            print('='*50)
            
            result = await client.get_weather(city)
            
            if result.get("status") == "success":
                data = result.get("data", {})
                print(f"✅ Success!")
                print(f"   City: {data.get('city', 'N/A')}")
                print(f"   Temperature: {data.get('temperature_c', 'N/A')}°C")
                print(f"   Wind Speed: {data.get('windspeed', 'N/A')} m/s")
                print(f"   Weather: {data.get('weather_description', 'N/A')}")
                print(f"   Coordinates: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
                print(f"   Provider: {data.get('provider', 'N/A')}")
            else:
                error = result.get("error", {})
                print(f"❌ Error: {error.get('code', 'Unknown')} - {error.get('message', 'Unknown error')}")
        
        # Test error handling with invalid city
        print(f"\n{'='*50}")
        print("Testing error handling with invalid city...")
        print('='*50)
        
        result = await client.get_weather("invalid_city_xyz_123")
        if result.get("status") == "error":
            error = result.get("error", {})
            print(f"❌ Expected error: {error.get('code', 'Unknown')} - {error.get('message', 'Unknown error')}")
        else:
            print("⚠️  Unexpected success for invalid city")
        
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")
        print(f"❌ Demo failed: {str(e)}")
    
    finally:
        # Disconnect from the server
        print("\nDisconnecting from server...")
        await client.disconnect()
        print("Demo completed!")


async def interactive_mode():
    """Interactive mode for testing weather queries."""
    client = WeatherClient()
    
    try:
        await client.connect()
        print("Weather Client Interactive Mode")
        print("=" * 40)
        print("Enter city names to get weather information.")
        print("Type 'quit' or 'exit' to stop.")
        print("=" * 40)
        
        while True:
            try:
                city = input("\nEnter city name: ").strip()
                
                if city.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not city:
                    print("Please enter a city name.")
                    continue
                
                print(f"Getting weather for {city}...")
                result = await client.get_weather(city)
                
                if result.get("status") == "success":
                    data = result.get("data", {})
                    print(f"\n✅ Weather for {data.get('city', city)}:")
                    print(f"   Temperature: {data.get('temperature_c', 'N/A')}°C")
                    print(f"   Wind Speed: {data.get('windspeed', 'N/A')} m/s")
                    print(f"   Weather: {data.get('weather_description', 'N/A')}")
                    print(f"   Coordinates: {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}")
                else:
                    error = result.get("error", {})
                    print(f"\n❌ Error: {error.get('message', 'Unknown error')}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
    
    finally:
        await client.disconnect()


def main():
    """Main entry point for the weather client."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FastMCP Weather Client")
    parser.add_argument(
        "--mode",
        choices=["demo", "interactive"],
        default="demo",
        help="Run mode: demo or interactive (default: demo)"
    )
    parser.add_argument(
        "--server",
        default="http://localhost:8010/sse",
        help="Server URL (default: http://localhost:8010/sse)"
    )
    
    args = parser.parse_args()
    
    # Update client server URL if provided
    if args.server != "http://localhost:8010/sse":
        WeatherClient.server_url = args.server
    
    try:
        if args.mode == "demo":
            asyncio.run(demo_weather_client())
        else:
            asyncio.run(interactive_mode())
    except KeyboardInterrupt:
        print("\nClient stopped by user")
    except Exception as e:
        logger.error(f"Client error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
