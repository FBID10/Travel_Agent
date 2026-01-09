import os
import requests
from google import genai
from google.genai import types
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini via Replit AI Integrations
AI_INTEGRATIONS_GEMINI_API_KEY = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY")
AI_INTEGRATIONS_GEMINI_BASE_URL = os.environ.get("AI_INTEGRATIONS_GEMINI_BASE_URL")

# Initialize the Gemini Client
client = genai.Client(
    api_key=AI_INTEGRATIONS_GEMINI_API_KEY,
    http_options={
        'api_version': 'v1beta',
        'base_url': AI_INTEGRATIONS_GEMINI_BASE_URL   
    }
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all apps to connect
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- Data Models ---
class TravelRequest(BaseModel):
    destination: str

# --- Helper Function ---
def get_weather_data(city_name: str):
    """Fetches weather data from Open-Meteo."""
    try:
        # 1. Geocoding
        city_quoted = city_name.replace(" ", "%20")
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_quoted}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        print(f"DEBUG: Geocoding response for {city_name}: {geo_res}")
        
        if not geo_res.get("results"):
            return None
        
        location = geo_res["results"][0]
        lat, lon = location["latitude"], location["longitude"]
        
        # 2. Weather Forecast (Daily)
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
        weather_res = requests.get(weather_url).json()
        print(f"DEBUG: Weather response: {weather_res}")
        
        if "daily" not in weather_res:
            return None
            
        # Parse today's forecast (Index 0)
        temp_max = weather_res["daily"]["temperature_2m_max"][0]
        temp_min = weather_res["daily"]["temperature_2m_min"][0]
        precip_prob = weather_res["daily"]["precipitation_probability_max"][0]
        
        return {
            "city": city_name,
            "country": location.get("country", ""),
            "temp_max": temp_max,
            "temp_min": temp_min,
            "precip_prob": precip_prob
        }
    except Exception as e:
        print(f"DEBUG: Exception in get_weather_data: {e}")
        return None

# --- NEW ENDPOINT: Get Raw Weather Data ---
@app.get("/weather/{city}")
def get_weather_endpoint(city: str):
    """Fetches raw weather data without AI advice."""
    data = get_weather_data(city)
    if not data:
        raise HTTPException(status_code=404, detail="City not found")
    return data

# --- ENDPOINT: Get AI Travel Advice ---
@app.post("/travel_advice")
async def travel_advice(request: TravelRequest):
    # Step 1: Call get_weather_data
    weather_data = get_weather_data(request.destination)
    if not weather_data:
        raise HTTPException(status_code=404, detail="Weather data not found for destination")
    
    # Step 2: Construct prompt
    weather_info = (f"Destination: {weather_data['city']}, {weather_data['country']}. "
                    f"Forecast: Max {weather_data['temp_max']}°C, Min {weather_data['temp_min']}°C, "
                    f"Precipitation Probability: {weather_data['precip_prob']}%.")
    
    prompt = (f"Act as a Travel Advisor. Based on the following destination and weather info, "
              f"provide clothing and travel recommendations. Do NOT use asterisks for bolding. "
              f"Instead, put the topic at the start of the line, followed by a relevant emoji, "
              f"then the description. Use clear headings (using ###):\n\n{weather_info}")
    
    # Step 3: Ask Gemini
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        advice = response.text
    except Exception as e:
        print(f"AI Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Agent error: {str(e)}")
    
    # Step 4: Return JSON
    return {
        "advice": advice,
        "weather": weather_data
    }

# --- Frontend (HTML) ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Travel Advisor</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --primary-hover: #4f46e5;
                --bg: #fdfdfe;
                --card-bg: #ffffff;
                --text-main: #1e293b;
                --text-muted: #64748b;
                --accent: #f5f7ff;
            }
            * { box-sizing: border-box; }
            body { 
                font-family: 'Inter', sans-serif; 
                background-color: var(--bg);
                color: var(--text-main);
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
                letter-spacing: -0.01em;
            }
            .container {
                background: var(--card-bg);
                width: 100%;
                max-width: 600px;
                padding: 48px;
                border-radius: 32px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            }
            header { text-align: center; margin-bottom: 40px; }
            .icon { font-size: 56px; margin-bottom: 20px; display: block; opacity: 0.9; }
            h1 { font-size: 28px; font-weight: 600; margin: 0 0 10px 0; color: var(--text-main); letter-spacing: -0.02em; }
            p { font-size: 15px; color: var(--text-muted); margin: 0; font-weight: 400; }
            .search-box {
                display: flex;
                flex-direction: column;
                gap: 14px;
                margin-bottom: 40px;
            }
            input {
                padding: 18px 24px;
                border: 1px solid #f1f5f9;
                background-color: #f8fafc;
                border-radius: 16px;
                font-size: 16px;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                outline: none;
                color: var(--text-main);
            }
            input:focus { 
                background-color: white;
                border-color: var(--primary); 
                box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.05); 
            }
            input::placeholder { color: #cbd5e1; }
            button {
                padding: 18px;
                background-color: var(--text-main);
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
            }
            button:hover { background-color: #000; transform: translateY(-1px); }
            button:active { transform: translateY(0); }
            #result {
                margin-top: 40px;
                font-size: 16px;
                line-height: 1.6;
                display: none;
                color: #334155;
            }
            #result h3 {
                color: var(--text-main);
                font-size: 18px;
                font-weight: 600;
                margin-top: 32px;
                margin-bottom: 16px;
                letter-spacing: -0.01em;
            }
            #result h3:first-child { margin-top: 0; }
            .weather-summary {
                background: var(--accent);
                padding: 24px;
                border-radius: 20px;
                margin-bottom: 32px;
                display: flex;
                justify-content: space-between;
                text-align: center;
            }
            .weather-item { display: flex; flex-direction: column; gap: 4px; flex: 1; }
            .weather-label { font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 600; letter-spacing: 0.05em; }
            .weather-value { font-size: 20px; font-weight: 600; color: var(--text-main); }
            .loading { 
                text-align: center;
                color: var(--text-muted);
                padding: 60px 0;
                font-size: 16px;
            }
            .spinner {
                width: 24px;
                height: 24px;
                border: 2px solid #f1f5f9;
                border-top: 2px solid var(--text-main);
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin: 0 auto 16px auto;
            }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .weather-badge {
                display: inline-block;
                padding: 6px 14px;
                background: var(--text-main);
                color: white;
                border-radius: 30px;
                font-weight: 500;
                margin-bottom: 24px;
                font-size: 13px;
            }
            li { margin-bottom: 12px; position: relative; padding-left: 20px; list-style: none; }
            li::before { 
                content: ""; 
                position: absolute; 
                left: 0; 
                top: 10px; 
                width: 4px; 
                height: 4px; 
                background: #cbd5e1; 
                border-radius: 50%; 
            }
            p { margin-bottom: 1.5em; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <span class="icon">🌍</span>
                <h1>Travel Advisor</h1>
                <p>Smart recommendations by Gemini 1.5</p>
            </header>
            <div class="search-box">
                <input type="text" id="destination" placeholder="Where is your next adventure?">
                <button id="btnAdvice" onclick="getAdvice()">Generate My Plan</button>
            </div>
            <div id="result"></div>
        </div>

        <script>
            function formatMarkdown(text) {
                if (!text) return "";
                let lines = text.split("\\n");
                let html = "";
                for (let line of lines) {
                    if (line.startsWith("### ")) {
                        html += "<h3>" + line.substring(4) + "</h3>";
                    } else if (line.trim().startsWith("* ")) {
                        html += "<li>" + line.trim().substring(2) + "</li>";
                    } else if (line.trim().startsWith("- ")) {
                        html += "<li>" + line.trim().substring(2) + "</li>";
                    } else if (line.includes("**")) {
                        let parts = line.split("**");
                        let boldLine = "";
                        for (let i = 0; i < parts.length; i++) {
                            boldLine += parts[i];
                            if (i < parts.length - 1) {
                                boldLine += (i % 2 === 0) ? "<strong>" : "</strong>";
                            }
                        }
                        html += boldLine + "<br>";
                    } else if (line.trim() === "") {
                        html += "<p></p>";
                    } else {
                        html += line + "<br>";
                    }
                }
                return html;
            }

            async function getAdvice() {
                const dest = document.getElementById('destination').value;
                if (!dest) return;
                
                const resultDiv = document.getElementById('result');
                const btn = document.getElementById('btnAdvice');
                
                btn.disabled = true;
                btn.innerText = 'Planning...';
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div><span>✨ Crafting your perfect trip...</span></div>';
                
                try {
                    const response = await fetch('/travel_advice', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ destination: dest })
                    });
                    const data = await response.json();
                    if (data.advice) {
                        let header = '';
                        if (data.weather) {
                            const w = data.weather;
                            header = `<div class="weather-badge">📍 ${w.city}, ${w.country}</div>\\n` +
                                     `<div class="weather-summary">` +
                                     `<div class="weather-item"><span class="weather-label">Max</span><span class="weather-value">${w.temp_max}°C</span></div>` +
                                     `<div class="weather-item"><span class="weather-label">Min</span><span class="weather-value">${w.temp_min}°C</span></div>` +
                                     `<div class="weather-item"><span class="weather-label">Rain</span><span class="weather-value">${w.precip_prob}%</span></div>` +
                                     `</div>`;
                        }
                        resultDiv.innerHTML = header + '<div style="margin-top:20px">' + formatMarkdown(data.advice) + '</div>';
                    } else {
                        resultDiv.innerText = 'Error: ' + (data.detail || 'Could not get advice');
                    }
                } catch (e) {
                    resultDiv.innerText = 'Error connecting to server';
                } finally {
                    btn.disabled = false;
                    btn.innerText = 'Generate My Plan';
                }
            }
        </script>
    </body>
    </html>
    """