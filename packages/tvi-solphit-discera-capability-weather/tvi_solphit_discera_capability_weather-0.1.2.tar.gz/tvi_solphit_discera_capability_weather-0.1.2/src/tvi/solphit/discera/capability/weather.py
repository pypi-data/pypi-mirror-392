# weather_capability.py

import requests
import re
from typing import Dict, Any, List, AsyncGenerator
from tvi.solphit.base.logging import SolphitLogger

log = SolphitLogger.get_logger("discera.capabilities.weather")

class WeatherCapability:
    """
    Capability: weather
    Purpose:
      Provides accurate, up-to-date weather forecasts for any location, including multi-day outlooks.
      Best for questions about current conditions, short-term forecasts, and weather trends.
    Primary intents:
      - "weather_forecast": multi-day forecast for a location
      - "current_weather": current conditions
      - "weather_trend": temperature, precipitation, wind trends
    Inputs:
      - question: user text (e.g., "weather in New York next 3 days")
      - history: prior turns (optional)
      - hints: location, date range, units
    Outputs:
      - answer: summarized weather forecast
      - contexts: list of API sources or links
      - meta: capability name, location, forecast details
    Examples:
      - "What is the weather going to be like in New York for the next 3 days?"
      - "Show me the temperature trend in Los Angeles this week."
      - "Is it going to rain in Chicago tomorrow?"
    """

    name = "weather"

    @staticmethod
    def descriptor() -> Dict[str, Any]:
        return {
            "name": "weather",
            "description": (
                "Provides accurate, up-to-date weather forecasts for any location, including multi-day outlooks. "
                "Best for questions about current conditions, short-term forecasts, and weather trends."
            ),
            "intents": ["weather_forecast", "current_weather", "weather_trend"],
            "examples": [
                "What is the weather going to be like in New York for the next 3 days?",
                "Show me the temperature trend in Los Angeles this week.",
                "Is it going to rain in Chicago tomorrow?"
            ],
            "tags": ["weather", "forecast", "trend", "current", "location", "temperature", "rain"],
            "excludes": ["climate", "climatology", "koppen"],
        }


    def run_once(self, args: Any, **kwargs) -> Dict[str, Any]:
        q: str = (getattr(args, "question", None) or args.get("question") or "").strip()
        hints: Dict[str, Any] = kwargs.get("hints") or {}

        # --- Extract location and days from question ---
        location = hints.get("location") or "New York"
        days = 3
        m = re.search(r"in ([A-Za-z\s]+)", q)
        if m:
            location = m.group(1).strip()
        m = re.search(r"next (\d+) days", q)
        if m:
            days = int(m.group(1))
        if days < 1 or days > 7:
            days = 3  # Open-Meteo allows up to 7 days

        # --- Geocode location to lat/lon ---
        geo_resp = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
        )
        geo = geo_resp.json()
        if not geo.get("results"):
            answer = f"Could not find location: {location}"
            return {"answer": answer, "contexts": [], "meta": {"capability": self.name, "location": location}}

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        # --- Get weather forecast for next N days ---
        weather_resp = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode&forecast_days={days}&timezone=auto"
        )
        weather = weather_resp.json()
        daily = weather.get("daily", {})
        dates = daily.get("time", [])
        temps_max = daily.get("temperature_2m_max", [])
        temps_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        codes = daily.get("weathercode", [])

        # --- Summarize forecast ---
        answer = f"Weather forecast for {location} (next {days} days):\n"
        for i in range(min(days, len(dates))):
            answer += (
                f"{dates[i]}: {temps_min[i]}°C to {temps_max[i]}°C, "
                f"precipitation: {precip[i]}mm, "
                f"weather code: {codes[i]}\n"
            )
        if not dates:
            answer += "(No forecast data found.)"
        return {
            "answer": answer,
            "contexts": [
                "https://open-meteo.com/",
                "https://open-meteo.com/en/docs"
            ],
            "meta": {
                "capability": self.name,
                "location": location,
                "days": days,
                "forecast": daily,
            },
        }

    async def run_stream(self, args: Any, **kwargs) -> AsyncGenerator[dict, None]:
        result = self.run_once(args, **kwargs)
        text = result["answer"]
        yield {"event": "generation_started", "data": {"capability": self.name}}
        for chunk in _chunk_text(text, max_len=64):
            yield {"event": "token", "data": chunk}
        yield {"event": "generation_done", "data": {}}
        yield {"event": "done", "data": {}}

def _chunk_text(s: str, max_len: int = 64) -> List[str]:
    out: List[str] = []
    buf = s.strip()
    while buf:
        out.append(buf[:max_len])
        buf = buf[max_len:]
    return out

def register(registry):
    registry.register(WeatherCapability())