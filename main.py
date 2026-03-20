import os
import csv
import json
from datetime import datetime

from weather_app.config import Config
from weather_app.weather_api import (
    WeatherAPIError, NetworkError,
    get_current_weather, get_forecast,
    search_cities, get_location_by_ip, clear_cache,
)
from weather_app.weather_parser import CurrentWeather, WeatherForecast, convert_temperature
from weather_app.weather_display import (
    display_current_weather, display_forecast,
    display_hourly_forecast, display_comparison,
    display_alert, display_success, display_info, display_help,
)


def _ensure_dirs():
    os.makedirs(Config.CACHE_DIR, exist_ok=True)
    os.makedirs(Config.DATA_DIR, exist_ok=True)


def _load_favorites():
    if not os.path.exists(Config.FAVORITES_FILE):
        return []
    try:
        with open(Config.FAVORITES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_favorites(favorites):
    with open(Config.FAVORITES_FILE, "w") as f:
        json.dump(favorites, f, indent=2)


def _ask_city(prompt="Enter city name: "):
    return input(prompt).strip()


def _suggest_and_pick(query):
    suggestions = search_cities(query)
    if not suggestions:
        return query
    print()
    print("  Suggestions:")
    for i, place in enumerate(suggestions, 1):
        state = f", {place.get('state', '')}" if place.get("state") else ""
        print(f"  {i}. {place['name']}{state}, {place['country']}")
    print(f"  {len(suggestions) + 1}. Use '{query}' as entered")
    print()
    choice = input("  Pick a number (or press Enter to use first result): ").strip()
    if not choice:
        p = suggestions[0]
        return f"{p['name']}, {p['country']}"
    try:
        idx = int(choice) - 1
        if idx == len(suggestions):
            return query
        if 0 <= idx < len(suggestions):
            p = suggestions[idx]
            return f"{p['name']}, {p['country']}"
    except ValueError:
        pass
    return query


def menu_current_weather(units):
    city = _ask_city()
    if not city:
        return
    city = _suggest_and_pick(city)
    try:
        raw = get_current_weather(city, units)
        display_current_weather(CurrentWeather(raw, units))
    except (WeatherAPIError, NetworkError) as exc:
        display_alert(str(exc))


def menu_forecast(units):
    city = _ask_city()
    if not city:
        return
    city = _suggest_and_pick(city)
    try:
        raw = get_forecast(city, units)
        display_forecast(WeatherForecast(raw, units))
    except (WeatherAPIError, NetworkError) as exc:
        display_alert(str(exc))


def menu_hourly(units):
    city = _ask_city()
    if not city:
        return
    city = _suggest_and_pick(city)
    try:
        raw = get_forecast(city, units)
        forecast = WeatherForecast(raw, units)
        days = list(forecast.by_day().keys())
        print()
        for i, d in enumerate(days):
            print(f"  {i + 1}. {d.strftime('%A, %d %B')}")
        choice = input("\n  Select day number: ").strip()
        try:
            day_index = int(choice) - 1
        except ValueError:
            day_index = 0
        display_hourly_forecast(forecast, day_index)
    except (WeatherAPIError, NetworkError) as exc:
        display_alert(str(exc))


def menu_compare(units):
    raw_input = input("  Enter city names separated by commas: ").strip()
    cities = [c.strip() for c in raw_input.split(",") if c.strip()]
    if len(cities) < 2:
        display_alert("Please enter at least two cities.")
        return
    weather_list = []
    for city in cities:
        try:
            raw = get_current_weather(city, units)
            weather_list.append(CurrentWeather(raw, units))
        except (WeatherAPIError, NetworkError) as exc:
            display_alert(f"{city}: {exc}")
    if weather_list:
        display_comparison(weather_list)


def menu_favorites(units):
    favorites = _load_favorites()
    print()
    print("  Favourite Cities:")
    if not favorites:
        print("  (none saved)")
    for i, city in enumerate(favorites, 1):
        print(f"  {i}. {city}")
    print()
    print("  a - add city")
    print("  r - remove city")
    print("  v - view weather for all favourites")
    print("  b - back")
    choice = input("\n  Choice: ").strip().lower()

    if choice == "a":
        city = _ask_city("  City to add: ")
        if city and city not in favorites:
            favorites.append(city)
            _save_favorites(favorites)
            display_success(f"Added '{city}' to favourites.")
    elif choice == "r":
        city = _ask_city("  City to remove: ")
        if city in favorites:
            favorites.remove(city)
            _save_favorites(favorites)
            display_success(f"Removed '{city}' from favourites.")
        else:
            display_alert(f"'{city}' not in favourites.")
    elif choice == "v":
        if not favorites:
            display_alert("No favourites saved.")
            return
        weather_list = []
        for city in favorites:
            try:
                raw = get_current_weather(city, units)
                weather_list.append(CurrentWeather(raw, units))
            except (WeatherAPIError, NetworkError) as exc:
                display_alert(f"{city}: {exc}")
        if weather_list:
            display_comparison(weather_list)


def menu_detect_location(units):
    display_info("Detecting location from IP address...")
    city = get_location_by_ip()
    if not city:
        display_alert("Could not detect location. Try entering a city manually.")
        return
    display_info(f"Detected location: {city}")
    try:
        raw = get_current_weather(city, units)
        display_current_weather(CurrentWeather(raw, units))
    except (WeatherAPIError, NetworkError) as exc:
        display_alert(str(exc))


def menu_export_csv(units):
    city = _ask_city()
    if not city:
        return
    try:
        raw = get_current_weather(city, units)
        weather = CurrentWeather(raw, units)
        filename = f"weather_{weather.city.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(Config.DATA_DIR, filename)
        fields = [
            ("City", weather.city),
            ("Country", weather.country),
            ("Observed At", weather.observed_at.isoformat()),
            (f"Temperature (deg{weather.temp_unit})", weather.temp),
            (f"Feels Like (deg{weather.temp_unit})", weather.feels_like),
            (f"Min Temp (deg{weather.temp_unit})", weather.temp_min),
            (f"Max Temp (deg{weather.temp_unit})", weather.temp_max),
            ("Humidity (%)", weather.humidity),
            ("Pressure (hPa)", weather.pressure),
            (f"Wind Speed ({weather.speed_unit})", weather.wind_speed),
            ("Wind Direction", weather.wind_direction),
            ("Cloudiness (%)", weather.cloudiness),
            ("Visibility (km)", weather.visibility),
            ("Condition", weather.description),
        ]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Field", "Value"])
            writer.writerows(fields)
        display_success(f"Exported to {filepath}")
    except (WeatherAPIError, NetworkError) as exc:
        display_alert(str(exc))


def menu_change_units(current_units):
    print()
    print("  1. Metric      (Celsius, m/s)")
    print("  2. Imperial    (Fahrenheit, mph)")
    print("  3. Standard    (Kelvin, m/s)")
    choice = input("\n  Select units: ").strip()
    mapping = {"1": "metric", "2": "imperial", "3": "standard"}
    new_units = mapping.get(choice)
    if new_units:
        display_success(f"Units changed to {new_units}.")
        return new_units
    display_alert("Invalid choice.")
    return current_units


def menu_clear_cache():
    count = clear_cache()
    display_success(f"Cleared {count} cached file(s).")


def main():
    _ensure_dirs()
    try:
        Config.validate()
    except ValueError as exc:
        print(f"\n[ERROR] {exc}\n")
        return

    units = Config.DEFAULT_UNITS
    print("\n  Welcome to the Weather Dashboard")
    print("  Type '?' or '0' for help/exit.\n")

    while True:
        print("\n" + "-" * 40)
        print("  1. Current weather")
        print("  2. 5-day forecast")
        print("  3. Hourly breakdown")
        print("  4. Compare cities")
        print("  5. Favourite cities")
        print("  6. Detect my location")
        print("  7. Export to CSV")
        print("  8. Change units")
        print("  9. Clear cache")
        print("  ?. Help")
        print("  0. Exit")
        print("-" * 40)

        choice = input("  Select option: ").strip()

        if choice == "0":
            print("\n  Goodbye!\n")
            break
        elif choice == "1":
            menu_current_weather(units)
        elif choice == "2":
            menu_forecast(units)
        elif choice == "3":
            menu_hourly(units)
        elif choice == "4":
            menu_compare(units)
        elif choice == "5":
            menu_favorites(units)
        elif choice == "6":
            menu_detect_location(units)
        elif choice == "7":
            menu_export_csv(units)
        elif choice == "8":
            units = menu_change_units(units)
        elif choice == "9":
            menu_clear_cache()
        elif choice == "?":
            display_help()
        else:
            display_alert("Invalid option. Try again.")


if __name__ == "__main__":
    main()