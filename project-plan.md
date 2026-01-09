# Project Plan - Multi-Agent Weather Advisor

This document outlines the step-by-step implementation plan for the Multi-Agent Weather Advisor. Following these steps results in a fully functional system with two agents communicating via the generic Agent-to-Agent (A2A) protocol.

### 1. Environment Setup
*   **Install Tools**: Ensure **Python 3.12+** and **uv** (package manager) are installed.
*   **Initialize Project**: Run `uv init` to create the project structure.
*   **Install Dependencies**: Add `google-adk[a2a]`, `uvicorn`, `fastapi`, and `python-dotenv`.
*   **Configure Authentication**: Create a `.env` file containing your `GOOGLE_API_KEY` (obtained from Google AI Studio). *Note: Vertex AI variables like project ID are not required for this setup.*

### 2. Project Structure
*   **Create Directories**: Set up folders for `weather_agent` and `travel_planner`.
*   **Verify Config**: Ensure `pyproject.toml` reflects the installed dependencies and `.env` is properly formatted.

### 3. Implement Weather Agent (The Service)
*   **Create Agent Logic**: In `weather_agent/agent.py`, define the `WeatherAgent`.
*   **Implement Tool**: script the `get_weather` function (mock tool) to provide forecasts.
*   **Expose via A2A**: Use `to_a2a` to wrap the agent as a FastAPI application.
*   **Web UI Support**: Assign the agent to a `root_agent` variable to make it discoverable by the ADK Web UI.
*   **Configuration**: Set the agent to run on **port 8000** by default (standard for ADK agent cards).

### 4. Implement Travel Planner (The Client)
*   **Create Agent Logic**: In `travel_planner/agent.py`, define the `TravelPlanner` agent.
*   **Connect to Remote Agent**: Configure a `RemoteA2aAgent` ("weather_service") pointing to `http://127.0.0.1:8000`.
*   **System Prompt**: Instruct the TravelPlanner to delegate weather queries to the `weather_service`.
*   **Web UI Support**: Expose `root_agent` in `travel_planner/agent.py`.
*   **CLI Runner**: Create `main_agent.py` in the root directory to run the TravelPlanner in the terminal, connecting to the same remote agent.

### 5. Execution & Verification
This system supports two running modes.

**Option A: Command Line Interface (CLI)**
1.  **Start Service**: Run the WeatherAgent service using `uvicorn` on port 8000.
2.  **Run Client**: Execute `main_agent.py` to prompt the TravelPlanner and see the A2A interaction in the console.

**Option B: ADK Web UI**
1.  **Start Service**: Run the WeatherAgent service using `uvicorn` on port 8000.
2.  **Start UI**: Run `adk web` on **port 9000** (to avoid port conflict with the service).
3.  **Interact**: Open the browser at `http://localhost:9000`, select `travel_planner_agent`, and chat.
