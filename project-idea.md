# Multi-Agent Weather Advisor

> [!IMPORTANT]
> **Requirement**: You need a **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/). Do not use a generic Google Cloud API Key.

## 🌟 Overview

This project demonstrates a **multi-agent system** where two specialized AI agents collaborate to help users plan trips based on the weather. It is built using:
*   **Google ADK (Agent Development Kit)**: The core framework for defining agents.
*   **Agent-to-Agent (A2A) Protocol**: The standard protocol for agents to discover and talk to each other.

## 🤖 The Agents (What We Built)

The system consists of two distinct agents working together:

### 1. Travel Planner (The Main Agent)
*   **Role**: The friendly, user-facing assistant.
*   **Job**: It takes your travel questions (e.g., "I'm going to London, what should I pack?").
*   **Superpower**: It knows it *doesn't* know the weather. Instead of guessing, it knows exactly who to ask: the **Weather Agent**.

### 2. Weather Agent (The Specialist)
*   **Role**: A background service provider.
*   **Job**: It answers specific questions about weather forecasts.
*   **Superpower**: It has ample access to a `get_weather` tool (simulated in this project) that provides accurate data. It does not chat with users directly; it chats with other agents.

---

## 🔄 How It Works

1.  **User asks**: "Should I bring an umbrella to Paris on Sunday?"
2.  **Travel Planner thinks**: "I need weather info for Paris on Sunday. I will ask the Weather Service."
3.  **A2A Call**: The Travel Planner sends a structured request over the network to the Weather Agent.
4.  **Tool Execution**: The Weather Agent receives the request, runs its `get_weather` tool, and finds out it's "rainy".
5.  **Response**: The Weather Agent replies to the Planner: "It will be rainy."
6.  **Final Answer**: The Travel Planner tells the user: "Yes, bring an umbrella because it's going to be rainy in Paris."

## 🏗️ Why This Architecture?

*   **Specialization**: Each agent does one thing well. The Planner focuses on advice; the Weather Agent focuses on data.
*   **Scalability**: The Weather Agent runs as a separate service (on port 8000). It could technically be hosted on a different server entirely.
*   **Interoperability**: By using the **A2A Protocol**, any other agent (not just ours) could discover and use the Weather Agent service just by reading its "Agent Card."

## 🚀 Key Technologies
*   **ADK & FastAPI**: For creating the agents and serving them over HTTP.
*   **Gemini 1.5/2.0**: The LLM brains powering the reasoning.
*   **MCP (Model Context Protocol)**: The standard used for defining the `get_weather` tool so the AI knows how to use it safely.
