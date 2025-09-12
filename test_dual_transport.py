#!/usr/bin/env python3
"""Test script for dual transport (SSE + WebSocket) server."""

import asyncio
import json
import logging
import httpx
import websockets
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DualTransportTester:
    """Test both SSE and WebSocket connections."""
    
    def __init__(self, base_url: str = "http://192.168.1.37:8010"):
        self.base_url = base_url
        self.sse_url = f"{base_url}/sse"
        self.websocket_url = f"ws://192.168.1.37:8010/mcp_endpoint/mcp/"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_health_endpoint(self):
        """Test the health check endpoint."""
        logger.info("Testing health endpoint...")
        try:
            response = await self.client.get(f"{self.base_url}/mcp_endpoint/health")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Health check successful: {data}")
                return True
            else:
                logger.error(f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False
    
    async def test_root_endpoint(self):
        """Test the root endpoint."""
        logger.info("Testing root endpoint...")
        try:
            response = await self.client.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Root endpoint successful: {data}")
                return True
            else:
                logger.error(f"Root endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Root endpoint error: {e}")
            return False
    
    async def test_sse_connection(self):
        """Test SSE connection."""
        logger.info("Testing SSE connection...")
        try:
            async with self.client.stream(
                "GET",
                self.sse_url,
                headers={
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache"
                }
            ) as response:
                if response.status_code == 200:
                    logger.info("SSE connection established successfully")
                    # Read a few lines to verify it's working
                    count = 0
                    async for line in response.aiter_lines():
                        if line.startswith('data: '):
                            logger.info(f"SSE data received: {line}")
                            count += 1
                            if count >= 2:  # Read 2 messages then stop
                                break
                    return True
                else:
                    logger.error(f"SSE connection failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"SSE connection error: {e}")
            return False
    
    async def test_websocket_connection(self):
        """Test WebSocket connection."""
        logger.info("Testing WebSocket connection...")
        try:
            # Test tool endpoint with correct token
            tool_url = f"{self.websocket_url}?token=default_key_123456"
            async with websockets.connect(tool_url) as websocket:
                logger.info("Tool WebSocket connection established successfully")
                
                # Send a test message
                test_message = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "ping",
                    "params": {}
                }
                await websocket.send(json.dumps(test_message))
                logger.info("Test message sent via Tool WebSocket")
                
                # Wait for response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    logger.info(f"Tool WebSocket response received: {response}")
                except asyncio.TimeoutError:
                    logger.warning("Tool WebSocket response timeout (expected without tool agent)")
            
            # Test robot endpoint with correct token
            robot_url = f"ws://192.168.1.37:8010/mcp_endpoint/call/?token=default_key_123456"
            async with websockets.connect(robot_url) as websocket:
                logger.info("Robot WebSocket connection established successfully")
                
                # Send a test message
                test_message = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }
                await websocket.send(json.dumps(test_message))
                logger.info("Test message sent via Robot WebSocket")
                
                # Wait for response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    logger.info(f"Robot WebSocket response received: {response}")
                except asyncio.TimeoutError:
                    logger.warning("Robot WebSocket response timeout (expected without tool agent)")
            
            return True  # Both connections were successful
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests."""
        logger.info("Starting dual transport tests...")
        
        results = {
            "health_endpoint": await self.test_health_endpoint(),
            "root_endpoint": await self.test_root_endpoint(),
            "sse_connection": await self.test_sse_connection(),
            "websocket_connection": await self.test_websocket_connection(),
        }
        
        logger.info("Test results:")
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            logger.info(f"  {test_name}: {status}")
        
        all_passed = all(results.values())
        logger.info(f"Overall result: {'PASS' if all_passed else 'FAIL'}")
        
        return all_passed

async def main():
    """Main test function."""
    tester = DualTransportTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
