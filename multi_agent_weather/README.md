# Multi-Agent Weather Advisor

A multi-agent system built with **Google Agent Development Kit (ADK)** using the **Agent-to-Agent (A2A)** protocol. This project demonstrates how specialized agents (like a Weather Agent) can communicate and collaborate to solve user queries.

## 🏗️ Architecture

The system consists of two primary agents:

1.  **WeatherAgent** (`weather_agent/agent.py`)
    *   **Role**: Specialized service provider.
    *   **Function**: Provides (mock) weather forecasts using a strict internal tool `get_weather`.
    *   **Tech**: Runs as a local service (FastAPI) exposing endpoints via the A2A protocol.
    *   **Model**: Uses `gemini-2.0-flash-exp`.

2.  **TravelPlanner** (`main_agent.py` or `travel_planner/agent.py`)
    *   **Role**: Main user-facing assistant.
    *   **Function**: Helps users plan trips. Connects to `WeatherAgent` to fetch real-time weather data when needed.
    *   **Tech**: Uses `RemoteA2aAgent` client to send requests to the WeatherAgent service.

## 📇 Agent Card

The **Weather Agent** publishes its metadata (capabilities, tools) at a standard "well-known" URL. When running locally on port 8000:

*   **URL**: `http://localhost:8000/.well-known/agent-card.json`

## 🛠️ Prerequisites

*   **Python**: v3.12+
*   **Package Manager**: `uv` (recommended)
*   **API Key**: A **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).

## 🚀 Setup

1.  **Clone/Open** the project directory.
2.  **Install Dependencies**:
    ```bash
    uv sync
    # OR manual install:
    uv add google-adk[a2a] uvicorn fastapi python-dotenv
    ```
3.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=AIzaSy...<your_key>...
    ```
    *Note: Do NOT set `GOOGLE_CLOUD_PROJECT` or `GOOGLE_CLOUD_LOCATION` if using AI Studio keys.*

## 💻 How to Run

You can run the system in two modes: **Terminal (CLI)** or **Web UI**.

### Option 1: Terminal (Simple CLI)

This runs the interaction independently in your console.

1.  **Start the Weather Service** (Terminal 1):
    Running on port **8000** (default).
    ```bash
    uv run uvicorn weather_agent.agent:a2a_app --host 0.0.0.0 --port 8000
    ```

2.  **Run the Main Agent** (Terminal 2):
    This script connects to the service on port 8000 and simulates a user conversation.
    ```bash
    uv run python main_agent.py
    ```

### Option 2: ADK Web UI (Visual Interface)

This uses Google's experimental ADK Web UI for a rich chat experience.

1.  **Start the Weather Service** (Terminal 1):
    Run on port **8000** to match the agent card configuration.
    ```bash
    uv run uvicorn weather_agent.agent:a2a_app --host 0.0.0.0 --port 8000
    ```

2.  **Start the ADK Web UI** (Terminal 2):
    Run on port **9000** to avoid conflict with the Weather Service.
    ```bash
    uv run adk web . --port 9000
    ```

3.  **Chat**:
    *   Open `http://localhost:9000` in your browser.
    *   Select **`travel_planner_agent`** from the dropdown.
    *   Type: *"I'm going to London tomorrow. Do I need a coat?"*

## ❓ Why Run All This?

*   **Decoupling**: The WeatherAgent can be hosted anywhere (remote server), scalable independently of the Planner.
*   **Specialization**: The WeatherAgent knows *how* to call the API; the Planner just knows *who* to ask.
*   **Standardization**: Uses the A2A standard for discovery (`.well-known/agent-card.json`) and communication.

## 🐛 Troubleshooting

*   **Port Conflicts**: If `Address already in use`, make sure to stop old processes (CTRL+C) or use `taskkill`.
*   **API Key Errors**: Ensure your `.env` has a valid `GOOGLE_API_KEY` and *no* conflicting Vertex AI variables.
*   **Connection Refused**: Ensure the WeatherAgent is actually running on the specific port (8000) expected by the client.
