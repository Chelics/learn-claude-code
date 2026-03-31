#!/usr/bin/env python3
"""
Weather MCP Server

A Model Context Protocol server that provides weather information
tools for Claude. Uses OpenWeatherMap API to fetch real-time weather data.
"""

import os
import json
import asyncio
import httpx
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# Create server instance
weather_server = Server("weather-server")

# Configuration
API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")
BASE_URL = "https://api.openweathermap.org/data/2.5"

@weather_server.tool()
async def get_current_weather(city: str, units: str = "metric") -> str:
    """
    Get current weather information for a city.
    
    Args:
        city: The city name (e.g., "London", "New York", "Tokyo")
        units: Temperature units ("metric" for Celsius, "imperial" for Fahrenheit)
    
    Returns:
        A formatted string with weather information
    """
    if not API_KEY or API_KEY == "your_api_key_here":
        return "Error: OpenWeatherMap API key not configured. Please set OPENWEATHER_API_KEY environment variable."
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/weather",
                params={
                    "q": city,
                    "appid": API_KEY,
                    "units": units,
                    "lang": "en"
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                return f"Error: Failed to fetch weather data (Status: {response.status_code})"
            
            data = response.json()
            
            # Extract weather information
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind_speed = data["wind"]["speed"]
            weather_desc = data["weather"][0]["description"]
            country = data["sys"]["country"]
            
            unit_symbol = "°C" if units == "metric" else "°F"
            wind_unit = "m/s" if units == "metric" else "mph"
            
            result = f"""🌤️ Weather in {city}, {country}:

🌡️ Temperature: {temp}{unit_symbol} (feels like {feels_like}{unit_symbol})
💧 Humidity: {humidity}%
📊 Pressure: {pressure} hPa
💨 Wind Speed: {wind_speed} {wind_unit}
☁️ Condition: {weather_desc.capitalize()}"""
            
            return result
            
    except httpx.TimeoutException:
        return f"Error: Request timeout. The weather service is taking too long to respond."
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"

@weather_server.tool()
async def get_weather_forecast(city: str, days: int = 3, units: str = "metric") -> str:
    """
    Get weather forecast for the next few days.
    
    Args:
        city: The city name
        days: Number of days to forecast (1-5)
        units: Temperature units ("metric" or "imperial")
    
    Returns:
        A formatted forecast string
    """
    if not API_KEY or API_KEY == "your_api_key_here":
        return "Error: OpenWeatherMap API key not configured. Please set OPENWEATHER_API_KEY environment variable."
    
    if not 1 <= days <= 5:
        return "Error: Days must be between 1 and 5"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/forecast",
                params={
                    "q": city,
                    "appid": API_KEY,
                    "units": units,
                    "lang": "en",
                    "cnt": days * 8  # 8 data points per day (3-hour intervals)
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                return f"Error: Failed to fetch forecast data (Status: {response.status_code})"
            
            data = response.json()
            
            unit_symbol = "°C" if units == "metric" else "°F"
            
            result = f"📅 {days}-Day Weather Forecast for {city}:\n\n"
            
            # Group forecasts by day
            daily_forecasts = {}
            for item in data["list"]:
                date = item["dt_txt"].split(" ")[0]
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(item)
            
            # Process each day
            for i, (date, forecasts) in enumerate(list(daily_forecasts.items())[:days]):
                temps = [f["main"]["temp"] for f in forecasts]
                min_temp = min(temps)
                max_temp = max(temps)
                conditions = [f["weather"][0]["description"] for f in forecasts]
                most_common_condition = max(set(conditions), key=conditions.count)
                
                result += f"Day {i+1} ({date}): {min_temp}{unit_symbol} - {max_temp}{unit_symbol}, {most_common_condition.capitalize()}\n"
            
            return result
            
    except httpx.TimeoutException:
        return f"Error: Request timeout. The weather service is taking too long to respond."
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"

@weather_server.tool()
async def get_air_quality(latitude: float, longitude: float) -> str:
    """
    Get current air quality index for a location.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns:
        Air quality information
    """
    if not API_KEY or API_KEY == "your_api_key_here":
        return "Error: OpenWeatherMap API key not configured. Please set OPENWEATHER_API_KEY environment variable."
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://api.openweathermap.org/data/2.5/air_pollution",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": API_KEY
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                return f"Error: Failed to fetch air quality data (Status: {response.status_code})"
            
            data = response.json()
            aqi = data["list"][0]["main"]["aqi"]
            components = data["list"][0]["components"]
            
            # AQI scale
            aqi_levels = {
                1: "Good 👍",
                2: "Fair 👌",
                3: "Moderate 😐",
                4: "Poor 😷",
                5: "Very Poor 🤢"
            }
            
            result = f"🌫️ Air Quality Index: {aqi_levels.get(aqi, 'Unknown')}\n\n"
            result += "Pollutant Levels (μg/m³):\n"
            result += f"• PM2.5: {components.get('pm2_5', 0)}\n"
            result += f"• PM10: {components.get('pm10', 0)}\n"
            result += f"• NO₂: {components.get('no2', 0)}\n"
            result += f"• SO₂: {components.get('so2', 0)}\n"
            result += f"• CO: {components.get('co', 0)} μg/m³\n"
            result += f"• O₃: {components.get('o3', 0)}\n"
            
            return result
            
    except httpx.TimeoutException:
        return f"Error: Request timeout. The air quality service is taking too long to respond."
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"

@weather_server.tool()
async def search_cities(query: str, limit: int = 5) -> str:
    """
    Search for cities by name to get their coordinates.
    
    Args:
        query: City name to search for
        limit: Maximum number of results
    
    Returns:
        List of matching cities with coordinates
    """
    if not API_KEY or API_KEY == "your_api_key_here":
        return "Error: OpenWeatherMap API key not configured. Please set OPENWEATHER_API_KEY environment variable."
    
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
            
            if response.status_code != 200:
                return f"Error: Failed to search cities (Status: {response.status_code})"
            
            data = response.json()
            
            if not data:
                return f"No cities found matching '{query}'"
            
            result = f"🔍 Found {len(data)} city(ies) matching '{query}':\n\n"
            
            for i, city in enumerate(data, 1):
                name = city["name"]
                country = city.get("country", "N/A")
                state = city.get("state", "N/A")
                lat = city["lat"]
                lon = city["lon"]
                
                result += f"{i}. {name}, {country}"
                if state != "N/A":
                    result += f", {state}"
                result += f"\n   Coordinates: {lat:.2f}, {lon:.2f}\n\n"
            
            return result
            
    except httpx.TimeoutException:
        return f"Error: Request timeout. The search service is taking too long to respond."
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"

# Main function to run the server
async def main():
    async with stdio_server() as (read, write):
        await weather_server.run(read, write)

if __name__ == "__main__":
    asyncio.run(main())
