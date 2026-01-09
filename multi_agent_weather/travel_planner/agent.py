from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
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

# 1. Reference to the remote WeatherAgent (assuming it runs on port 8000)
# We run WeatherAgent on 8000 to match its default card config.
# We will run ADK Web UI on 9000.
weather_agent_url = "http://127.0.0.1:8000"

weather_service = RemoteA2aAgent(
    name="weather_service",
    description="Remote weather info agent (via A2A)",
    agent_card=f"{weather_agent_url}{AGENT_CARD_WELL_KNOWN_PATH}"
)

# 2. Define the system prompt for the main TravelPlanner agent
MAIN_PROMPT = """You are a travel planning assistant. 
Your job is to help users plan trips and outdoor activities. 
If the user asks about weather or whether they should bring certain items (like an umbrella), 
you must consult the weather_service agent for the latest weather info.
To do this, you will ask the weather_service for a forecast. 
Include the information you get in your answer to the user.
If the question is not about weather, answer it directly from your knowledge.
Be concise and helpful.
"""

# 3. Create the main agent
travel_planner_agent = Agent(
    name="travel_planner_agent",
    model="gemini-2.5-flash", # Updated to gemini-2.5-flash as requested
    instruction=MAIN_PROMPT,
    sub_agents=[ weather_service ]
)

# Expose for ADK Web UI
root_agent = travel_planner_agent
