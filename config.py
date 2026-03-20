import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL = "https://api.openweathermap.org/geo/1.0"
    DEFAULT_CITY = os.getenv("DEFAULT_CITY", "London")
    DEFAULT_UNITS = os.getenv("DEFAULT_UNITS", "metric")
    CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "600"))
    CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    FAVORITES_FILE = os.path.join(DATA_DIR, "favorites.json")
    REQUEST_TIMEOUT = 10

    UNIT_LABELS = {
        "metric":   {"temp": "C", "speed": "m/s"},
        "imperial": {"temp": "F", "speed": "mph"},
        "standard": {"temp": "K", "speed": "m/s"},
    }

    WEATHER_ICONS = {
        "Clear":        "[SUN]",
        "Clouds":       "[CLOUD]",
        "Rain":         "[RAIN]",
        "Drizzle":      "[DRIZZLE]",
        "Thunderstorm": "[STORM]",
        "Snow":         "[SNOW]",
        "Mist":         "[MIST]",
        "Smoke":        "[SMOKE]",
        "Haze":         "[HAZE]",
        "Dust":         "[DUST]",
        "Fog":          "[FOG]",
        "Sand":         "[SAND]",
        "Ash":          "[ASH]",
        "Squall":       "[SQUALL]",
        "Tornado":      "[TORNADO]",
    }

    @classmethod
    def validate(cls):
        if not cls.API_KEY:
            raise ValueError(
                "API key not found. Set OPENWEATHER_API_KEY in your .env file.\n"
                "Get a free key at: https://openweathermap.org/api"
            )
        if cls.DEFAULT_UNITS not in ("metric", "imperial", "standard"):
            raise ValueError("DEFAULT_UNITS must be metric, imperial, or standard.")