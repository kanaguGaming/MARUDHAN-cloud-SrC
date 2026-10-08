import json
import urllib.request
import asyncio
import logging

logger = logging.getLogger("WEATHER_API")

def _fetch_sync(lat: float, lon: float) -> dict:
    # Open-Meteo is a free, no-API-key required weather service perfectly suited for this.
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    req = urllib.request.Request(url, headers={'User-Agent': 'MARUDHAN_OS/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=5.0) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                current = data.get("current_weather", {})
                return {
                    "temperature_c": current.get("temperature"),
                    "wind_speed_kmh": current.get("windspeed"),
                    "wind_direction": current.get("winddirection"),
                    "is_day": current.get("is_day"),
                    "status": "success"
                }
    except Exception as e:
        logger.error(f"Weather API Fetch Error: {e}")
        
    # Fallback baseline data if offline/fails
    return {
        "temperature_c": 32.0,
        "wind_speed_kmh": 12.0,
        "wind_direction": 90,
        "is_day": 1,
        "status": "fallback"
    }

async def fetch_live_weather(lat: float = 11.1085, lon: float = 77.3411) -> dict:
    """
    Fetches live weather data from external API for the farm's location asynchronously.
    Default coordinates are mapped to central Tamil Nadu (e.g. Tiruppur region).
    """
    return await asyncio.to_thread(_fetch_sync, lat, lon)
