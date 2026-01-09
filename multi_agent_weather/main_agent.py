from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
from google.genai.types import Content, Part
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# Debug: Print loaded env vars (masked)
api_key = os.getenv("GOOGLE_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")
project = os.getenv("GOOGLE_CLOUD_PROJECT")
print(f"DEBUG: GOOGLE_API_KEY={api_key[:4] if api_key else 'None'}...{api_key[-4:] if api_key else ''}")
print(f"DEBUG: GEMINI_API_KEY={gemini_key[:4] if gemini_key else 'None'}...{gemini_key[-4:] if gemini_key else ''}")
print(f"DEBUG: GOOGLE_CLOUD_PROJECT={project}")

# Force Gemini API (AI Studio) by removing Vertex AI configs
if "GOOGLE_CLOUD_PROJECT" in os.environ:
    del os.environ["GOOGLE_CLOUD_PROJECT"]
if "GOOGLE_CLOUD_LOCATION" in os.environ:
    del os.environ["GOOGLE_CLOUD_LOCATION"]
if "GOOGLE_CLOUD_REGION" in os.environ:
    del os.environ["GOOGLE_CLOUD_REGION"]
    
print("DEBUG: Unset Vertex AI env vars to force Gemini API usage.")

# 1. Reference to the remote WeatherAgent (ensure WeatherAgent is running at localhost:8000)
# weather_agent_url = f"http://127.0.0.1:8000{AGENT_CARD_WELL_KNOWN_PATH}"
weather_agent_url = "http://127.0.0.1:8000"

weather_service = RemoteA2aAgent(
    name="weather_service",
    description="Remote weather info agent (via A2A)",
    agent_card=f"http://127.0.0.1:8000{AGENT_CARD_WELL_KNOWN_PATH}"
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
    model="gemini-2.5-flash",
    instruction=MAIN_PROMPT,
    sub_agents=[ weather_service ]
)

# 4. Test the agent with a sample query
if __name__ == "__main__":
    import asyncio
    
    async def main():
        user_question = "I'm going to Paris on Sunday. Should I carry an umbrella?"
        print(f"User: {user_question}")
        
        try:
            # Create a session service
            session_service = InMemorySessionService()
            
            # Wrap the agent in a Runner
            runner = Runner(
                agent=travel_planner_agent, 
                session_service=session_service,
                app_name="travel_planner_app"
            )

            # Create the session first
            await session_service.create_session(
                app_name="travel_planner_app",
                user_id="test-user",
                session_id="test-session"
            )
            
            # Construct the message using google.genai.types.Content
            new_message = Content(role="user", parts=[Part(text=user_question)])
            
            # Runner.run returns a generator of events (it's synchronous wrapper over async)
            # But the session creation needed to be async.
            # wait, if Runner.run is sync, maybe session creation is stuck?
            # Let's check if create_session is actually async. 
            # Based on error 'RuntimeWarning: coroutine ... was never awaited', yes it is.
            
            events = runner.run(
                user_id="test-user",
                session_id="test-session",
                new_message=new_message
            )
            
            print("Assistant Response Events:")
            for event in events:
                # We are looking for the final answer which usually comes as a part in a model event
                # or we can just print everything for debugging the flow.
                if hasattr(event, 'content') and event.content:
                    for part in event.content.parts:
                        if part.text:
                            print(f"Assistant Part: {part.text}")
                
        except Exception as e:
            print(f"Error running agent: {e}")

    asyncio.run(main())
