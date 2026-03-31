# MCP Server Build Guide

## ✅ Project Complete!

I've successfully built an MCP (Model Context Protocol) server for you! Here's what was created:

### 📁 Files Created

1. **`simple_mcp_server.py`** - The main MCP weather server (demo mode works without API key)
2. **`main.py`** - Alternative version using MCP SDK (when available)
3. **`README.md`** - Comprehensive usage documentation
4. **`requirements.txt`** - Dependencies
5. **`.env`** & **`.env.example`** - Configuration files
6. **`mcp.json`** - Claude configuration snippet
7. **`test_server.py`** - Test script
8. **`BUILD_GUIDE.md`** - This file

### 🛠️ Tools Provided

Your weather server includes 4 powerful tools:

#### 1. `get_current_weather`
- Get real-time weather for any city
- Supports Celsius (metric) or Fahrenheit (imperial)
- Returns temperature, conditions, humidity, wind speed

**Usage:**
```python
get_current_weather("Tokyo", "metric")
```

#### 2. `get_weather_forecast`
- 1-5 day weather forecast
- Detailed daily conditions
- Temperature ranges

**Usage:**
```python
get_weather_forecast("New York", 3, "imperial")
```

#### 3. `search_cities`
- Find cities by name
- Get coordinates for air quality lookups
- Multiple results with location details

**Usage:**
```python
search_cities("San", 5)
```

#### 4. `get_air_quality` (in main.py)
- Air Quality Index (AQI)
- Pollutant levels (PM2.5, PM10, NO₂, etc.)
- Health recommendations

### 🚀 Quick Start

#### Option 1: Test Immediately (Demo Mode)

The server works in demo mode without an API key:

```bash
cd mcp-weather-server

# Test with sample data
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 simple_mcp_server.py
```

✅ **You can use the server immediately!**

#### Option 2: Real Weather Data

1. **Get API Key** (Free):
   - Visit: https://openweathermap.org/api
   - Sign up for free account
   - Get your API key (activates in 10 minutes)

2. **Configure**:
   ```bash
   # Edit .env file
   OPEN_WEATHER_API_KEY=your_actual_key_here
   ```

3. **Use with Claude**:
   
   Edit `~/.claude/mcp.json`:
   ```json
   {
     "mcpServers": {
       "weather": {
         "command": "python3",
         "args": ["/path/to/mcp-weather-server/simple_mcp_server.py"],
         "env": {
           "OPEN_WEATHER_API_KEY": "your_actual_key_here"
         }
       }
     }
   }
   ```

### 💡 Key Features

✅ **Standard MCP Protocol** - JSON-RPC over stdio  
✅ **Clean Error Handling** - Timeout, API errors, validation  
✅ **Async Operations** - Non-blocking I/O  
✅ **Demo Mode** - Works without API key  
✅ **Type Hints** - Clean, maintainable code  
✅ **Documentation** - Clear docstrings  

### 🧪 Testing

Test the server manually:

```bash
# List available tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 simple_mcp_server.py

# Call a tool
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_current_weather","arguments":{"city":"Paris"}}}' | python3 simple_mcp_server.py
```

### 🔍 What is MCP?

Model Context Protocol (MCP) is Anthropic's open protocol that enables AI assistants like Claude to securely interact with external data sources and tools. It works like a **USB-C for AI applications** - standardized way to connect AI to data.

**How it works:**
```
Claude ↔ MCP Protocol ↔ Your Weather Server ↔ OpenWeatherMap API
```

### 📚 Next Steps

1. **Get your API key** and test with real data
2. **Customize tools** - Add new weather features
3. **Add caching** - Reduce API calls
4. **Add more data sources** - Multiple weather APIs
5. **Build TypeScript version** - Using @modelcontextprotocol/sdk

### 🎯 Real-World Usage Example

Once configured with Claude:

**User:** "What's the weather like in Tokyo and should I bring an umbrella?"

**Claude will:**
1. Call `get_current_weather("Tokyo", "metric")`
2. Call `get_weather_forecast("Tokyo", 1, "metric")`
3. Analyze and respond: "It's 22°C and partly cloudy in Tokyo. The forecast shows light rain tomorrow, so bring an umbrella!"

---

## 🌟 Your MCP Server is Ready!

Start building amazing AI-powered applications with real-time weather data. The MCP protocol opens up endless possibilities for connecting Claude to external services.

**Need something different?** I can help you build MCP servers for:
- Databases (PostgreSQL, MySQL, MongoDB)
- APIs (GitHub, Twitter, Slack)
- File systems
- Custom business logic
- IoT devices
- And much more!
