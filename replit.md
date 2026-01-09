# Multi-Agent Weather Advisor

## Overview
A multi-agent system built with Google Agent Development Kit (ADK) using the Agent-to-Agent (A2A) protocol. The system demonstrates how specialized agents (like a Weather Agent) can communicate and collaborate to solve user queries.

## Architecture
The system consists of two primary agents:

1. **WeatherAgent** (`multi_agent_weather/weather_agent/agent.py`)
   - Role: Specialized service provider
   - Function: Provides (mock) weather forecasts using a `get_weather` tool
   - Tech: Runs as a local service (FastAPI) exposing endpoints via the A2A protocol
   - Model: Uses `gemini-2.0-flash-exp`

2. **TravelPlanner** (`multi_agent_weather/travel_planner/agent.py`)
   - Role: Main user-facing assistant
   - Function: Helps users plan trips. Connects to WeatherAgent to fetch weather data when needed
   - Tech: Uses `RemoteA2aAgent` client to send requests to the WeatherAgent service

## How to Use
1. Select "travel_planner_agent" from the dropdown in the ADK Web UI
2. Ask a travel-related question like "I'm going to London tomorrow. Do I need an umbrella?"
3. The Travel Planner will consult the Weather Agent and provide advice

## Project Structure
- `multi_agent_weather/` - Main application directory
  - `weather_agent/` - Weather agent implementation
  - `travel_planner/` - Travel planner agent implementation
  - `main_agent.py` - CLI test script
  - `start.sh` - Startup script that runs both services
  - `pyproject.toml` - Python project configuration

## Technical Details
- **Language**: Python 3.12
- **Package Manager**: uv
- **Framework**: Google ADK, FastAPI, Uvicorn
- **Ports**: 
  - Port 5000: ADK Web UI (frontend)
  - Port 8000: Weather Agent A2A Service (internal)

## Environment Variables Required
- `GOOGLE_API_KEY`: Gemini API key from Google AI Studio

## Recent Changes
- Initial setup for Replit environment
- Updated pyproject.toml to support Python 3.12
- Created start.sh script for running both services
- Configured workflow for ADK Web UI on port 5000
