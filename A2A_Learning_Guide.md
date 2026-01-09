# 🎓 Learning Guide: Agent-to-Agent (A2A) Concepts
*A beginner-friendly tour of the Multi-Agent Weather Advisor project.*

Welcome! This guide explains the core concepts of the **Google Agent-to-Agent (A2A)** protocol and shows exactly how we implemented them in this project. 

Think of A2A as a **universal language** that lets AI agents talk to each other, even if they were built by different people or run on different computers.

---

## 1. The Core Concept: Client & Server Agents

A2A behaves like the web (HTTP). One agent acts as a **Client** (asking for help), and another acts as a **Server** (providing a service).

### Concept
*   **The Client**: The agent that has a goal but needs help. It sends a task to another agent.
*   **The Server (Remote Agent)**: The specialized agent that sits waiting for requests. It does the work and sends back the answer.

### 📍 In Our Project
*   **The Server**: Our `WeatherAgent` (`weather_agent/agent.py`). It waits for weather questions.
*   **The Client**: Our `TravelPlanner` (`main_agent.py` or `travel_planner/agent.py`). It plans trips but *calls* the `WeatherAgent` when it needs a forecast.

**Code Mapping (`main_agent.py`):**
```python
# We define the "client" connection here using RemoteA2aAgent
weather_service = RemoteA2aAgent(
    name="weather_service",
    # This URL points to the "Server" agent
    agent_card="http://127.0.0.1:8000/.well-known/agent-card.json"
)
```

---

## 2. The Agent Card (Discovery) 📇

How does one agent know what another agent can do? They read the **Agent Card**.

### Concept
The Agent Card is like a **resume** or a business card for an AI agent. It is a JSON file always located at `/.well-known/agent-card.json`. It tells the world:
1.  **Who I am** (Name, Description).
2.  **What I can do** (Tools/Capabilities).
3.  **How to talk to me** (API Endpoints).

### 📍 In Our Project
We didn't write a JSON file manually! The ADK generated it automatically from our code.

**Code Mapping (`weather_agent/agent.py`):**
```python
# We create the agent object
weather_agent = Agent(
    name="weather_agent",
    description="An agent that provides weather forecasts...",
    tools=[ get_weather ]  # <--- These tools go into the Agent Card!
)

# This single line creates the server AND the Agent Card automatically
a2a_app = to_a2a(weather_agent)
```
*When you run this agent, you can visit `http://127.0.0.1:8000/.well-known/agent-card.json` to see the generated card!*

---

## 3. A2A vs. MCP (Tools vs. Communication) 🛠️

You might hear about **MCP (Model Context Protocol)**. It’s important to know the difference.

### Concept
*   **MCP (Vertical)**: How an agent talks to its *own* tools (like a calculator or database). It's like a craftsman picking up a hammer.
*   **A2A (Horizontal)**: How an agent talks to *other agents*. It's like a craftsman calling a plumber.

**They work together!** An agent receives an **A2A** request, and then uses an **MCP** tool to solve it.

### 📍 In Our Project
Our `WeatherAgent` receives a request via **A2A**, but then it uses a Python function (`get_weather`) as a tool—this tool definition follows MCP principles (schemas, safe execution).

**Code Mapping (`weather_agent/agent.py`):**
```python
# This function acts as an MCP-style tool.
# The ADK reads the type hints (city: str) and docstring to understand how to use it.
def get_weather(city: str, date: str) -> str:
    """
    Returns a simple weather forecast...
    """
    # Logic happens here
    return "sunny"
```

---

## 4. Implicit Delegation (The "Orchestration") 🎼

How does the main agent know *when* to call the other agent?

### Concept
We don't write `if "weather" in question: call_agent()`. Instead, we give the AI a **System Prompt** (instructions). The LLM (Large Language Model) is smart enough to decide: *"I don't know the answer, but I have a sub-agent who does."*

### 📍 In Our Project
We specifically told the `TravelPlanner` about the `weather_service` and gave it instructions.

**Code Mapping (`main_agent.py`):**
```python
MAIN_PROMPT = """
You are a travel planning assistant.
...
If the user asks about weather... you **must** consult the weather_service agent...
"""

travel_planner_agent = Agent(
    ...
    instruction=MAIN_PROMPT,       # 1. The Instructions
    sub_agents=[ weather_service ] # 2. The Capability
)
```
*Because of this setup, the "Magic" happens automatically.*

---

## Summary Checklist ✅

| A2A Concept | How we did it |
| :--- | :--- |
| **Server Agent** | Created `weather_agent` running on port 8000. |
| **Client Agent** | Created `TravelPlanner` connected via `RemoteA2aAgent`. |
| **Discovery** | Used `to_a2a()` to verify the `.well-known/agent-card.json`. |
| **Protocol** | Used standard HTTP/JSON (hidden behind the ADK library). |
| **Collaboration** | The Planner delegated the "weather" part of the query to the specialist. |

---
*Run the project now and watch these concepts in action!*
