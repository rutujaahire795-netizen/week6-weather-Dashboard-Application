import os
import json
import time
import hashlib
import requests
from weather_app.config import Config


class WeatherAPIError(Exception):
    pass


class NetworkError(Exception):
    pass


def _cache_path(key):
    os.makedirs(Config.CACHE_DIR, exist_ok=True)
    safe_key = hashlib.md5(key.encode()).hexdigest()
    return os.path.join(Config.CACHE_DIR, f"{safe_key}.json")


def _read_cache(key):
    path = _cache_path(key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            entry = json.load(f)
        if time.time() - entry["timestamp"] < Config.CACHE_TTL:
            return entry["data"]
    except (json.JSONDecodeError, KeyError, OSError):
        pass
    return None


def _write_cache(key, data):
    path = _cache_path(key)
    try:
        with open(path, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
    except OSError:
        pass


def _get(endpoint, params):
    params["appid"] = Config.API_KEY
    cache_key = endpoint + json.dumps(params, sort_keys=True)
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached

    try:
        response = requests.get(
            f"{Config.BASE_URL}/{endpoint}",
            params=params,
            timeout=Config.REQUEST_TIMEOUT,
        )
    except requests.exceptions.ConnectionError:
        raise NetworkError("No internet connection. Check your network and try again.")
    except requests.exceptions.Timeout:
        raise NetworkError("Request timed out. The server took too long to respond.")
    except requests.exceptions.RequestException as exc:
        raise NetworkError(f"Network error: {exc}")

    if response.status_code == 401:
        raise WeatherAPIError("Invalid API key. Check your OPENWEATHER_API_KEY.")
    if response.status_code == 404:
        raise WeatherAPIError("City not found. Try a different city name.")
    if response.status_code == 429:
        raise WeatherAPIError("API rate limit exceeded. Wait a moment and try again.")
    if not response.ok:
        raise WeatherAPIError(f"API error {response.status_code}: {response.text}")

    data = response.json()
    _write_cache(cache_key, data)
    return data


def get_current_weather(city, units="metric"):
    return _get("weather", {"q": city, "units": units})


def get_forecast(city, units="metric"):
    return _get("forecast", {"q": city, "units": units})


def get_weather_by_coords(lat, lon, units="metric"):
    return _get("weather", {"lat": lat, "lon": lon, "units": units})


def get_forecast_by_coords(lat, lon, units="metric"):
    return _get("forecast", {"lat": lat, "lon": lon, "units": units})


def search_cities(query, limit=5):
    try:
        params = {"q": query, "limit": limit, "appid": Config.API_KEY}
        response = requests.get(
            f"{Config.GEO_URL}/direct",
            params=params,
            timeout=Config.REQUEST_TIMEOUT,
        )
        if response.ok:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return []


def get_location_by_ip():
    try:
        response = requests.get("https://ipapi.co/json/", timeout=5)
        if response.ok:
            data = response.json()
            city = data.get("city")
            country = data.get("country_name")
            if city:
                return f"{city}, {country}" if country else city
    except requests.exceptions.RequestException:
        pass
    return None


def clear_cache():
    if not os.path.exists(Config.CACHE_DIR):
        return 0
    count = 0
    for filename in os.listdir(Config.CACHE_DIR):
        if filename.endswith(".json"):
            try:
                os.remove(os.path.join(Config.CACHE_DIR, filename))
                count += 1
            except OSError:
                pass
    return count