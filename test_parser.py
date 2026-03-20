import unittest
from weather_app.weather_parser import (
    CurrentWeather, WeatherForecast,
    celsius_to_fahrenheit, fahrenheit_to_celsius,
    celsius_to_kelvin, convert_temperature,
)

SAMPLE_CURRENT = {
    "name": "Paris",
    "sys": {"country": "FR", "sunrise": 1700010000, "sunset": 1700050000},
    "main": {"temp": 20.0, "feels_like": 19.0, "temp_min": 17.0, "temp_max": 23.0, "humidity": 55, "pressure": 1015},
    "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
    "wind": {"speed": 3.0, "deg": 90},
    "visibility": 10000,
    "clouds": {"all": 5},
    "dt": 1700030000,
}

SAMPLE_FORECAST = {
    "city": {"name": "Paris", "country": "FR"},
    "list": [
        {
            "dt": 1700032000,
            "main": {"temp": 21.0, "feels_like": 20.0, "temp_min": 18.0, "temp_max": 24.0, "humidity": 50, "pressure": 1014},
            "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
            "wind": {"speed": 2.5, "deg": 100},
            "pop": 0.1,
        },
        {
            "dt": 1700118400,
            "main": {"temp": 18.0, "feels_like": 17.0, "temp_min": 15.0, "temp_max": 20.0, "humidity": 60, "pressure": 1012},
            "weather": [{"main": "Rain", "description": "light rain", "icon": "10d"}],
            "wind": {"speed": 4.0, "deg": 180},
            "pop": 0.7,
        },
    ],
}


class TestCurrentWeather(unittest.TestCase):
    def setUp(self):
        self.weather = CurrentWeather(SAMPLE_CURRENT, units="metric")

    def test_city_name(self):        self.assertEqual(self.weather.city, "Paris")
    def test_country(self):          self.assertEqual(self.weather.country, "FR")
    def test_temperature(self):      self.assertEqual(self.weather.temp, 20.0)
    def test_humidity(self):         self.assertEqual(self.weather.humidity, 55)
    def test_condition(self):        self.assertEqual(self.weather.condition, "Clear")
    def test_temp_unit_metric(self): self.assertEqual(self.weather.temp_unit, "C")
    def test_wind_direction_east(self): self.assertEqual(self.weather.wind_direction, "E")
    def test_icon_clear(self):       self.assertEqual(self.weather.icon, "[SUN]")
    def test_visibility_km(self):    self.assertAlmostEqual(self.weather.visibility, 10.0)


class TestWeatherForecast(unittest.TestCase):
    def setUp(self):
        self.forecast = WeatherForecast(SAMPLE_FORECAST, units="metric")

    def test_city(self):             self.assertEqual(self.forecast.city, "Paris")
    def test_slots_count(self):      self.assertEqual(len(self.forecast.slots), 2)

    def test_daily_summary_keys(self):
        summary = self.forecast.daily_summary()[0]
        for key in ("date", "temp_min", "temp_max", "condition", "icon", "pop"):
            self.assertIn(key, summary)


class TestTemperatureConversion(unittest.TestCase):
    def test_c_to_f(self):   self.assertAlmostEqual(celsius_to_fahrenheit(0), 32.0)
    def test_f_to_c(self):   self.assertAlmostEqual(fahrenheit_to_celsius(32), 0.0)
    def test_c_to_k(self):   self.assertAlmostEqual(celsius_to_kelvin(0), 273.15)
    def test_metric_to_imperial(self):  self.assertAlmostEqual(convert_temperature(0, "metric", "imperial"), 32.0)
    def test_imperial_to_metric(self):  self.assertAlmostEqual(convert_temperature(32, "imperial", "metric"), 0.0)
    def test_metric_to_standard(self):  self.assertAlmostEqual(convert_temperature(0, "metric", "standard"), 273.15)
    def test_same_unit(self):           self.assertEqual(convert_temperature(25, "metric", "metric"), 25)


if __name__ == "__main__":
    unittest.main()