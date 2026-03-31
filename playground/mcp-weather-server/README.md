# MCP Weather Server

A Model Context Protocol (MCP) server that provides real-time weather information tools for Claude.

## Features

- 🌤️ Get current weather for any city
- 📅 5-day weather forecast
- 🌫️ Air quality index lookup
- 🔍 Search cities by name
- 🌍 Multi-unit support (Celsius/Fahrenheit)

## Setup

### 1. Install Dependencies

```bash
cd mcp-weather-server
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get API Key

1. Sign up for a free API key at [OpenWeatherMap](https://openweathermap.org/api)
2. Open the `.env` file:

```bash
OPENWEATHER_API_KEY=your_actual_api_key_here
```

### 3. Test the Server

```bash
# Make the script executable
chmod +x main.py

# Test with MCP Inspector
npx @anthropics/mcp-inspector python3 main.py
```

## Tools Available

### get_current_weather
Get current weather for a city.

**Parameters:**
- `city` (string): The city name
- `units` (string, optional): "metric" (Celsius) or "imperial" (Fahrenheit)

**Example:**
```python
get_current_weather("London", "metric")
```

### get_weather_forecast
Get weather forecast for the next days.

**Parameters:**
- `city` (string): The city name
- `days` (int, optional): Number of days (1-5)
- `units` (string, optional): "metric" or "imperial"

**Example:**
```python
get_weather_forecast("New York", 3, "imperial")
```

### get_air_quality
Get air quality index for coordinates.

**Parameters:**
- `latitude` (float): Latitude coordinate
- `longitude` (float): Longitude coordinate

**Example:**
```python
get_air_quality(40.7128, -74.0060)  # New York City
```

### search_cities
Search for cities by name.

**Parameters:**
- `query` (string): City name to search
- `limit` (int, optional): Maximum number of results

**Example:**
```python
search_cities("San", 5)
```

## Configuration with Claude

Add to your `~/.claude/mcp.json` file:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python3",
      "args": ["/Users/bannie/Documents/code/Agent/learn-claude-code/mcp-weather-server/main.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

## Usage Example

Once configured, Claude can use these tools:

**User:** What's the weather like in Tokyo?

**Claude will call:** `get_current_weather("Tokyo", "metric")`

**Response:** "🌤️ Weather in Tokyo, JP: 🌡️ Temperature: 22°C (feels like 20°C)..."

## Error Handling

The server includes comprehensive error handling:

- Invalid API key detection
- Network timeout handling
- City not found errors
- Invalid parameter validation
- Rate limit awareness

## API Limits

OpenWeatherMap free tier includes:
- 60 calls/minute
- 1,000,000 calls/month

Monitor your usage at the [OpenWeatherMap dashboard](https://home.openweathermap.org/api_keys).

## License

MIT License

## Contributing

Feel free to submit issues and enhancement requests!
