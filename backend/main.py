from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    print("⚠️  API Key not found. Please add API_KEY to your .env file!")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Air Quality API is running 🚀"}

@app.get("/airquality/")
def get_air_quality(city: str = None, lat: float = None, lon: float = None):
    if not API_KEY:
        return {"error": "API key not found"}

    try:
        # 1️⃣ If city name provided, convert it to coordinates
        if city:
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
            geo_resp = requests.get(geo_url)
            if geo_resp.status_code != 200 or not geo_resp.json():
                return {"error": "City not found"}
            loc = geo_resp.json()[0]
            lat, lon = loc["lat"], loc["lon"]

        if not lat or not lon:
            return {"error": "Latitude and longitude are required"}

        # 2️⃣ Get AQI data
        air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        air_resp = requests.get(air_url)
        if air_resp.status_code != 200:
            return {"error": "Failed to fetch AQI data"}

        data = air_resp.json()
        return {
            "city": city,
            "location": {"latitude": lat, "longitude": lon},
            "air_quality": data
        }

    except Exception as e:
        return {"error": str(e)}
