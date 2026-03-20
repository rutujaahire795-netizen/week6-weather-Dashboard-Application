from datetime import datetime
from weather_app.config import Config


class CurrentWeather:
    def __init__(self, data, units="metric"):
        self.city = data["name"]
        self.country = data["sys"]["country"]
        self.units = units

        main = data["main"]
        self.temp = round(main["temp"], 1)
        self.feels_like = round(main["feels_like"], 1)
        self.temp_min = round(main["temp_min"], 1)
        self.temp_max = round(main["temp_max"], 1)
        self.humidity = main["humidity"]
        self.pressure = main["pressure"]

        wind = data.get("wind", {})
        self.wind_speed = wind.get("speed", 0)
        self.wind_deg = wind.get("deg", 0)
        self.wind_gust = wind.get("gust")

        weather = data["weather"][0]
        self.condition = weather["main"]
        self.description = weather["description"].capitalize()
        self.icon_code = weather["icon"]

        self.visibility = data.get("visibility", 0) / 1000
        self.cloudiness = data.get("clouds", {}).get("all", 0)

        self.sunrise = datetime.fromtimestamp(data["sys"]["sunrise"])
        self.sunset = datetime.fromtimestamp(data["sys"]["sunset"])
        self.observed_at = datetime.fromtimestamp(data["dt"])

        self.rain_1h = data.get("rain", {}).get("1h", 0)
        self.snow_1h = data.get("snow", {}).get("1h", 0)

    @property
    def temp_unit(self):
        return Config.UNIT_LABELS[self.units]["temp"]

    @property
    def speed_unit(self):
        return Config.UNIT_LABELS[self.units]["speed"]

    @property
    def icon(self):
        return Config.WEATHER_ICONS.get(self.condition, "[?]")

    @property
    def wind_direction(self):
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        index = round(self.wind_deg / 45) % 8
        return directions[index]


class ForecastDay:
    def __init__(self, slot, units="metric"):
        self.units = units
        self.datetime = datetime.fromtimestamp(slot["dt"])
        self.date = self.datetime.date()
        self.time = self.datetime.strftime("%H:%M")

        main = slot["main"]
        self.temp = round(main["temp"], 1)
        self.feels_like = round(main["feels_like"], 1)
        self.temp_min = round(main["temp_min"], 1)
        self.temp_max = round(main["temp_max"], 1)
        self.humidity = main["humidity"]
        self.pressure = main["pressure"]

        weather = slot["weather"][0]
        self.condition = weather["main"]
        self.description = weather["description"].capitalize()

        wind = slot.get("wind", {})
        self.wind_speed = wind.get("speed", 0)

        self.pop = round(slot.get("pop", 0) * 100)
        self.rain_3h = slot.get("rain", {}).get("3h", 0)
        self.snow_3h = slot.get("snow", {}).get("3h", 0)

    @property
    def temp_unit(self):
        return Config.UNIT_LABELS[self.units]["temp"]

    @property
    def icon(self):
        return Config.WEATHER_ICONS.get(self.condition, "[?]")


class WeatherForecast:
    def __init__(self, data, units="metric"):
        self.city = data["city"]["name"]
        self.country = data["city"]["country"]
        self.units = units
        self.slots = [ForecastDay(slot, units) for slot in data["list"]]

    def by_day(self):
        days = {}
        for slot in self.slots:
            days.setdefault(slot.date, []).append(slot)
        return days

    def daily_summary(self):
        summaries = []
        for date, slots in self.by_day().items():
            temps = [s.temp for s in slots]
            pops = [s.pop for s in slots]
            conditions = [s.condition for s in slots]
            most_common = max(set(conditions), key=conditions.count)
            summaries.append({
                "date": date,
                "temp_min": round(min(temps), 1),
                "temp_max": round(max(temps), 1),
                "condition": most_common,
                "icon": Config.WEATHER_ICONS.get(most_common, "[?]"),
                "pop": max(pops),
                "slots": slots,
            })
        return summaries


def celsius_to_fahrenheit(c):
    return round(c * 9 / 5 + 32, 1)

def fahrenheit_to_celsius(f):
    return round((f - 32) * 5 / 9, 1)

def celsius_to_kelvin(c):
    return round(c + 273.15, 1)

def convert_temperature(value, from_unit, to_unit):
    if from_unit == to_unit:
        return value
    if from_unit == "imperial":
        celsius = fahrenheit_to_celsius(value)
    elif from_unit == "standard":
        celsius = value - 273.15
    else:
        celsius = value
    if to_unit == "imperial":
        return celsius_to_fahrenheit(celsius)
    if to_unit == "standard":
        return celsius_to_kelvin(celsius)
    return round(celsius, 1)

def format_datetime(dt, fmt="%A, %d %B %Y %H:%M"):
    return dt.strftime(fmt)

def format_date(date, fmt="%A, %d %B"):
    return date.strftime(fmt)