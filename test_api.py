import unittest
from unittest.mock import patch, MagicMock
from weather_app.weather_api import WeatherAPIError, NetworkError, get_current_weather, get_forecast, search_cities

SAMPLE_CURRENT = {
    "name": "London",
    "sys": {"country": "GB", "sunrise": 1700000000, "sunset": 1700040000},
    "main": {"temp": 15.0, "feels_like": 13.5, "temp_min": 12.0, "temp_max": 17.0, "humidity": 70, "pressure": 1013},
    "weather": [{"main": "Clouds", "description": "overcast clouds", "icon": "04d"}],
    "wind": {"speed": 5.5, "deg": 220},
    "visibility": 10000,
    "clouds": {"all": 90},
    "dt": 1700020000,
}

SAMPLE_FORECAST = {
    "city": {"name": "London", "country": "GB"},
    "list": [{
        "dt": 1700020000,
        "main": {"temp": 14.0, "feels_like": 12.0, "temp_min": 12.0, "temp_max": 16.0, "humidity": 75, "pressure": 1012},
        "weather": [{"main": "Rain", "description": "light rain", "icon": "10d"}],
        "wind": {"speed": 4.0, "deg": 200},
        "pop": 0.6,
    }],
}


class TestGetCurrentWeather(unittest.TestCase):

    @patch("weather_app.weather_api.requests.get")
    @patch("weather_app.weather_api._read_cache", return_value=None)
    @patch("weather_app.weather_api._write_cache")
    def test_success(self, mock_write, mock_read, mock_get):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = SAMPLE_CURRENT
        mock_get.return_value = mock_resp
        result = get_current_weather("London", "metric")
        self.assertEqual(result["name"], "London")

    @patch("weather_app.weather_api.requests.get")
    @patch("weather_app.weather_api._read_cache", return_value=None)
    def test_city_not_found(self, mock_read, mock_get):
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp
        with self.assertRaises(WeatherAPIError):
            get_current_weather("NotARealCity999", "metric")

    @patch("weather_app.weather_api.requests.get")
    @patch("weather_app.weather_api._read_cache", return_value=None)
    def test_invalid_api_key(self, mock_read, mock_get):
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 401
        mock_get.return_value = mock_resp
        with self.assertRaises(WeatherAPIError) as ctx:
            get_current_weather("London", "metric")
        self.assertIn("Invalid API key", str(ctx.exception))

    @patch("weather_app.weather_api.requests.get")
    @patch("weather_app.weather_api._read_cache", return_value=None)
    def test_network_error(self, mock_read, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.ConnectionError()
        with self.assertRaises(NetworkError):
            get_current_weather("London", "metric")

    @patch("weather_app.weather_api._read_cache", return_value=SAMPLE_CURRENT)
    def test_returns_cached_data(self, mock_read):
        result = get_current_weather("London", "metric")
        self.assertEqual(result["name"], "London")


class TestSearchCities(unittest.TestCase):

    @patch("weather_app.weather_api.requests.get")
    def test_returns_list(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = [{"name": "London", "country": "GB", "lat": 51.5, "lon": -0.1}]
        mock_get.return_value = mock_resp
        results = search_cities("Lon")
        self.assertEqual(results[0]["name"], "London")

    @patch("weather_app.weather_api.requests.get")
    def test_returns_empty_on_failure(self, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.ConnectionError()
        self.assertEqual(search_cities("xyz"), [])


if __name__ == "__main__":
    unittest.main()