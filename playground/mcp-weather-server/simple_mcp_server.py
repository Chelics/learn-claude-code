#!/usr/bin/env python3
"""
Simplified MCP Weather Server - Uses standard JSON-RPC over stdin/stdout
This demonstrates the MCP protocol without external dependencies.
"""

import os
import json
import asyncio
import httpx
import sys
from typing import Dict, Any, List

API_KEY = os.getenv("OPEN_WEATHER_API_KEY", "demo")
BASE_URL = "https://api.openweathermap.org/data/2.5"

class MCPWeatherServer:
    def __init__(self):
        self.tools = {}
        self.register_tools()
    
    def register_tools(self):
        """Register all available tools"""
        self.tools = {
            "get_current_weather": {
                "description": "Get current weather for a city",
                "parameters": {
                    "city": {"type": "string", "description": "City name"},
                    "units": {"type": "string", "description": "metric (C) or imperial (F)", "default": "metric"}
                }
            },
            "get_weather_forecast": {
                "description": "Get weather forecast for next days",
                "parameters": {
                    "city": {"type": "string", "description": "City name"},
                    "days": {"type": "integer", "description": "Days 1-5", "default": 3},
                    "units": {"type": "string", "description": "metric (C) or imperial (F)", "default": "metric"}
                }
            },
            "search_cities": {
                "description": "Search for cities by name",
                "parameters": {
                    "query": {"type": "string", "description": "City name to search"},
                    "limit": {"type": "integer", "description": "Max results", "default": 5}
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC requests"""
        try:
            method = request.get("method")
            request_id = request.get("id")
            
            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": name,
                                "description": tool["description"],
                                "inputSchema": {
                                    "type": "object",
                                    "properties": tool["parameters"],
                                    "required": [k for k, v in tool["parameters"].items() if "default" not in v]
                                }
                            }
                            for name, tool in self.tools.items()
                        ]
                    }
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                result = await self.execute_tool(tool_name, tool_args)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result}]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool with given arguments"""
        try:
            if tool_name == "get_current_weather":
                return await self.get_current_weather(
                    args.get("city", "London"),
                    args.get("units", "metric")
                )
            elif tool_name == "get_weather_forecast":
                return await self.get_weather_forecast(
                    args.get("city", "London"),
                    args.get("days", 3),
                    args.get("units", "metric")
                )
            elif tool_name == "search_cities":
                return await self.search_cities(
                    args.get("query", "London"),
                    args.get("limit", 5)
                )
            else:
                return f"Error: Unknown tool {tool_name}"
                
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    async def get_current_weather(self, city: str, units: str = "metric") -> str:
        """Get current weather"""
        if API_KEY == "demo":
            return f"🌤️ Demo Weather for {city}:\n🌡️ Temperature: 22°C\n☁️ Condition: Partly cloudy\n💨 Wind: 15 km/h\n\nTo use real weather data, set OPEN_WEATHER_API_KEY environment variable."
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BASE_URL}/weather",
                    params={
                        "q": city,
                        "appid": API_KEY,
                        "units": units
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    temp = data["main"]["temp"]
                    description = data["weather"][0]["description"]
                    unit_symbol = "°C" if units == "metric" else "°F"
                    
                    return f"🌤️ Weather in {city}:\n🌡️ Temperature: {temp}{unit_symbol}\n☁️ Condition: {description}"
                else:
                    return f"Error: Failed to fetch weather data (Status: {response.status_code})"
                    
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def get_weather_forecast(self, city: str, days: int = 3, units: str = "metric") -> str:
        """Get weather forecast"""
        if API_KEY == "demo":
            return f"📅 {days}-Day Demo Forecast for {city}:\n\nDay 1: 22°C - 25°C, Sunny\nDay 2: 20°C - 24°C, Partly Cloudy\nDay 3: 18°C - 22°C, Light Rain\n\nTo use real forecast data, set OPEN_WEATHER_API_KEY environment variable."
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BASE_URL}/forecast",
                    params={
                        "q": city,
                        "appid": API_KEY,
                        "units": units,
                        "cnt": days * 8
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = f"📅 {days}-Day Forecast for {city}:\n\n"
                    
                    for i in range(min(days, len(data["list"]) // 8)):
                        forecast = data["list"][i * 8]
                        temp = forecast["main"]["temp"]
                        description = forecast["weather"][0]["description"]
                        unit_symbol = "°C" if units == "metric" else "°F"
                        
                        result += f"Day {i+1}: {temp}{unit_symbol}, {description}\n"
                    
                    return result
                else:
                    return f"Error: Failed to fetch forecast data (Status: {response.status_code})"
                    
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def search_cities(self, query: str, limit: int = 5) -> str:
        """Search cities"""
        if API_KEY == "demo":
            return f"🔍 Demo Search Results for '{query}':\n\n1. {query.title()}, US\n2. {query.title()}, UK\n3. {query.title()}, CA\n\nTo search real cities, set OPEN_WEATHER_API_KEY environment variable."
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://api.openweathermap.org/geo/1.0/direct",
                    params={
                        "q": query,
                        "limit": limit,
                        "appid": API_KEY
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = f"🔍 Search Results for '{query}':\n\n"
                    
                    if not data:
                        return f"No cities found matching '{query}'"
                    
                    for i, city in enumerate(data, 1):
                        name = city["name"]
                        country = city.get("country", "N/A")
                        lat, lon = city["lat"], city["lon"]
                        
                        result += f"{i}. {name}, {country} ({lat:.2f}, {lon:.2f})\n"
                    
                    return result
                else:
                    return f"Error: Failed to search cities (Status: {response.status_code})"
                    
        except Exception as e:
            return f"Error: {str(e)}"

async def main():
    """Main function to run the MCP server"""
    server = MCPWeatherServer()
    
    # Read from stdin, write to stdout for MCP protocol
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            
            if not line:
                break
            
            # Parse JSON-RPC request
            request = json.loads(line.strip())
            
            # Handle the request
            response = await server.handle_request(request)
            
            # Send response
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            # Skip invalid JSON
            continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)}
            }))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
