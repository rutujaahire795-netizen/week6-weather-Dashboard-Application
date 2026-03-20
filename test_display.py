import unittest
from io import StringIO
from unittest.mock import patch
from weather_app.weather_display import display_current_weather, display_forecast, display_comparison, display_alert
from weather_app.weather_parser import CurrentWeather, WeatherForecast

SAMPLE_CURRENT = {
    "name": "Berlin", "sys": {"country": "DE", "sunrise": 1700010000, "sunset": 1700050000},
    "main": {"temp": 8.0, "feels_like": 6.0, "temp_min": 5.0, "temp_max": 10.0, "humidity": 80, "pressure": 1010},
    "weather": [{"main": "Clouds", "description": "broken clouds", "icon": "04d"}],
    "wind": {"speed": 6.0, "deg": 270}, "visibility": 9000, "clouds": {"all": 75}, "dt": 1700030000,
}

SAMPLE_FORECAST = {
    "city": {"name": "Berlin", "country": "DE"},
    "list": [{
        "dt": 1700032000,
        "main": {"temp": 9.0, "feels_like": 7.0, "temp_min": 6.0, "temp_max": 11.0, "humidity": 78, "pressure": 1009},
        "weather": [{"main": "Clouds", "description": "overcast clouds", "icon": "04n"}],
        "wind": {"speed": 5.5, "deg": 260}, "pop": 0.2,
    }],
}


class TestDisplayCurrentWeather(unittest.TestCase):
    def test_shows_city(self):
        w = CurrentWeather(SAMPLE_CURRENT, "metric")
        with patch("sys.stdout", new_callable=StringIO) as out:
            display_current_weather(w)
        self.assertIn("Berlin", out.getvalue())

    def test_shows_temperature(self):
        w = CurrentWeather(SAMPLE_CURRENT, "metric")
        with patch("sys.stdout", new_callable=StringIO) as out:
            display_current_weather(w)
        self.assertIn("8.0", out.getvalue())


class TestDisplayForecast(unittest.TestCase):
    def test_shows_city(self):
        f = WeatherForecast(SAMPLE_FORECAST, "metric")
        with patch("sys.stdout", new_callable=StringIO) as out:
            display_forecast(f)
        self.assertIn("Berlin", out.getvalue())


class TestDisplayAlert(unittest.TestCase):
    def test_shows_message(self):
        with patch("sys.stdout", new_callable=StringIO) as out:
            display_alert("Something went wrong")
        self.assertIn("Something went wrong", out.getvalue())


if __name__ == "__main__":
    unittest.main()