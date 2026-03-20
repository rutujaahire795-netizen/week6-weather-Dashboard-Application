from colorama import init, Fore, Style
from tabulate import tabulate
from weather_app.weather_parser import format_datetime, format_date

init(autoreset=True)

WEATHER_ART = {
    "Clear": r"""
     \   /
      .-.
   -(   )-
    `-'
""",
    "Clouds": r"""
      .--.
   .-(    ).
  (___.__)__)
""",
    "Rain": r"""
      .--.
   .-(    ).
  (___.__)__)
   ' ' ' '
""",
    "Drizzle": r"""
      .--.
   .-(    ).
  (___.__)__)
    . . .
""",
    "Thunderstorm": r"""
      .--.
   .-(    ).
  (___.__)__)
    /  /  /
""",
    "Snow": r"""
      .--.
   .-(    ).
  (___.__)__)
   * * * *
""",
    "Mist": r"""
  _ - _ - _ -
  _ - _ - _ -
  _ - _ - _ -
""",
}


def _temp_color(temp, unit="metric"):
    celsius = temp
    if unit == "imperial":
        celsius = (temp - 32) * 5 / 9
    elif unit == "standard":
        celsius = temp - 273.15
    if celsius <= 0:
        return Fore.CYAN
    if celsius <= 10:
        return Fore.BLUE
    if celsius <= 20:
        return Fore.GREEN
    if celsius <= 30:
        return Fore.YELLOW
    return Fore.RED


def _header(text):
    width = 60
    print()
    print(Fore.CYAN + Style.BRIGHT + "=" * width)
    print(Fore.CYAN + Style.BRIGHT + text.center(width))
    print(Fore.CYAN + Style.BRIGHT + "=" * width)


def _section(text):
    print()
    print(Fore.YELLOW + Style.BRIGHT + f"  -- {text} --")


def display_current_weather(weather):
    _header(f"Current Weather: {weather.city}, {weather.country}")

    art = WEATHER_ART.get(weather.condition, "")
    if art:
        for line in art.strip("\n").splitlines():
            print(Fore.WHITE + "  " + line)

    color = _temp_color(weather.temp, weather.units)
    print(
        f"\n  {weather.icon}  {weather.description}"
        f"  |  Observed: {format_datetime(weather.observed_at, '%H:%M, %d %b %Y')}"
    )
    print()
    print(
        f"  Temperature  : "
        + color + Style.BRIGHT + f"{weather.temp} deg{weather.temp_unit}"
        + Style.RESET_ALL
        + f"  (feels like {weather.feels_like} deg{weather.temp_unit})"
    )
    print(f"  High / Low   : {weather.temp_max} / {weather.temp_min} deg{weather.temp_unit}")
    print(f"  Humidity     : {weather.humidity}%")
    print(f"  Pressure     : {weather.pressure} hPa")
    print(f"  Wind         : {weather.wind_speed} {weather.speed_unit} {weather.wind_direction}", end="")
    if weather.wind_gust:
        print(f"  (gusts {weather.wind_gust} {weather.speed_unit})", end="")
    print()
    print(f"  Visibility   : {weather.visibility:.1f} km")
    print(f"  Cloud cover  : {weather.cloudiness}%")
    if weather.rain_1h:
        print(f"  Rain (1h)    : {weather.rain_1h} mm")
    if weather.snow_1h:
        print(f"  Snow (1h)    : {weather.snow_1h} mm")
    print()
    print(f"  Sunrise      : {weather.sunrise.strftime('%H:%M')}")
    print(f"  Sunset       : {weather.sunset.strftime('%H:%M')}")
    print()


def display_forecast(forecast):
    _header(f"5-Day Forecast: {forecast.city}, {forecast.country}")
    summaries = forecast.daily_summary()
    rows = []
    for day in summaries:
        color_lo = _temp_color(day["temp_min"], forecast.units)
        color_hi = _temp_color(day["temp_max"], forecast.units)
        unit_lbl = "C" if forecast.units == "metric" else ("F" if forecast.units == "imperial" else "K")
        rows.append([
            format_date(day["date"]),
            day["icon"],
            day["condition"],
            color_hi + f"{day['temp_max']}deg{unit_lbl}" + Style.RESET_ALL,
            color_lo + f"{day['temp_min']}deg{unit_lbl}" + Style.RESET_ALL,
            f"{day['pop']}%",
        ])
    headers = ["Date", "Icon", "Condition", "High", "Low", "Rain %"]
    print()
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    print()


def display_hourly_forecast(forecast, day_index=0):
    days = list(forecast.by_day().values())
    if day_index >= len(days):
        print(Fore.RED + "  No data for that day.")
        return
    slots = days[day_index]
    unit_lbl = "C" if forecast.units == "metric" else ("F" if forecast.units == "imperial" else "K")
    _header(f"Hourly Forecast: {slots[0].date.strftime('%A, %d %B')}")
    rows = []
    for slot in slots:
        color = _temp_color(slot.temp, forecast.units)
        rows.append([
            slot.time,
            slot.icon,
            slot.description,
            color + f"{slot.temp}deg{unit_lbl}" + Style.RESET_ALL,
            f"{slot.humidity}%",
            f"{slot.wind_speed} {forecast.units}",
            f"{slot.pop}%",
        ])
    headers = ["Time", "Icon", "Condition", "Temp", "Humidity", "Wind", "Rain %"]
    print()
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    print()


def display_comparison(weather_list):
    _header("City Comparison")
    rows = []
    for w in weather_list:
        color = _temp_color(w.temp, w.units)
        rows.append([
            f"{w.city}, {w.country}",
            color + f"{w.temp} deg{w.temp_unit}" + Style.RESET_ALL,
            f"{w.feels_like} deg{w.temp_unit}",
            f"{w.humidity}%",
            f"{w.wind_speed} {w.speed_unit}",
            w.description,
        ])
    headers = ["City", "Temp", "Feels Like", "Humidity", "Wind", "Condition"]
    print()
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    print()


def display_alert(message):
    print()
    print(Fore.RED + Style.BRIGHT + "  [!] " + message)
    print()

def display_success(message):
    print(Fore.GREEN + "  [OK] " + message)

def display_info(message):
    print(Fore.CYAN + "  [i] " + message)

def display_help():
    _header("Help")
    help_text = [
        ("1", "Current weather for a city"),
        ("2", "5-day forecast for a city"),
        ("3", "Hourly breakdown for a forecast day"),
        ("4", "Compare multiple cities"),
        ("5", "Manage favourite cities"),
        ("6", "Detect my location (by IP)"),
        ("7", "Export current weather to CSV"),
        ("8", "Change temperature units"),
        ("9", "Clear API cache"),
        ("0", "Exit"),
    ]
    print()
    print(tabulate(help_text, headers=["Option", "Description"], tablefmt="simple"))
    print()