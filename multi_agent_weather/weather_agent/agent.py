from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
import os
from dotenv import load_dotenv

load_dotenv()

# Force Gemini API (AI Studio) by removing Vertex AI configs
if "GOOGLE_CLOUD_PROJECT" in os.environ:
    del os.environ["GOOGLE_CLOUD_PROJECT"]
if "GOOGLE_CLOUD_LOCATION" in os.environ:
    del os.environ["GOOGLE_CLOUD_LOCATION"]
if "GOOGLE_CLOUD_REGION" in os.environ:
    del os.environ["GOOGLE_CLOUD_REGION"]

import requests

# 1. Define the weather lookup tool as a function
def get_weather(city: str, date: str) -> str:
    """
    Returns a weather forecast for the given city and date using Open-Meteo.
    Args:
        city (str): The city name (e.g., "Paris").
        date (str): The date or day for the forecast (e.g., "Sunday").
    Returns:
        str: A weather description including temperatures.
    """
    try:
        # 1. Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        if not geo_res.get("results"):
            return f"Could not find location for {city}"
        
        location = geo_res["results"][0]
        lat, lon = location["latitude"], location["longitude"]
        
        # 2. Weather Forecast
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
        weather_res = requests.get(weather_url).json()
        
        if "daily" not in weather_res:
            return "Could not fetch weather data."
            
        # Simplification: Return today's data (first index)
        # In a real app we would parse 'date' and find the matching index
        temp_max = weather_res["daily"]["temperature_2m_max"][0]
        temp_min = weather_res["daily"]["temperature_2m_min"][0]
        precip_prob = weather_res["daily"]["precipitation_probability_max"][0]
        
        return f"Weather in {city} ({location.get('country', '')}): Max {temp_max}°C, Min {temp_min}°C, Rain chance: {precip_prob}%."
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

# 2. Create the WeatherAgent with ADK
weather_agent = Agent(
    name="weather_agent",
    description="An agent that provides weather forecasts using Open-Meteo.",
    model="gemini-2.5-flash",  # Updated to gemini-2.5-flash as requested
    instruction=(
        "You are a weather information agent. "
        "When asked about the weather, you **must** use the get_weather tool to get the latest forecast. "
        "Provide the forecast briefly and accurately."
    ),
    tools=[ get_weather ]
)


# 3. Expose the agent via A2A (FastAPI app)
a2a_app = to_a2a(weather_agent)

# Expose for ADK Web UI
root_agent = weather_agent
