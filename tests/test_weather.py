import pytest
import os
from unittest.mock import patch, MagicMock
from weather_service.server import WeatherServer, WeatherData, RateLimiter
import time
import requests

@pytest.fixture
def weather_server():
    # Ensure we have a mock API key for tests
    os.environ["OPENWEATHER_API_KEY"] = "test_key"
    return WeatherServer()

@pytest.fixture
def mock_weather_response():
    return {
        "main": {
            "temp": 20.5,
            "humidity": 65,
            "feels_like": 19.8,
            "pressure": 1013
        },
        "weather": [
            {"description": "clear sky"}
        ],
        "wind": {
            "speed": 5.2
        },
        "clouds": {
            "all": 20
        },
        "dt": int(time.time())
    }

@pytest.fixture
def mock_forecast_response():
    return {
        "list": [
            {
                "dt_txt": "2024-03-20 12:00:00",
                "main": {
                    "temp": 22.5,
                    "humidity": 70
                },
                "weather": [
                    {"description": "sunny"}
                ]
            },
            {
                "dt_txt": "2024-03-21 12:00:00",
                "main": {
                    "temp": 21.0,
                    "humidity": 75
                },
                "weather": [
                    {"description": "partly cloudy"}
                ]
            }
        ]
    }

@pytest.mark.asyncio
async def test_get_current_weather(weather_server, mock_weather_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_weather_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        resource = await weather_server.get_current_weather({"city": "London"})
        
        assert resource.data["temperature"] == 20.5
        assert resource.data["description"] == "clear sky"
        assert resource.data["humidity"] == 65
        assert resource.data["wind_speed"] == 5.2
        assert resource.metadata["city"] == "London"
        assert resource.metadata["unit"] == "metric"

@pytest.mark.asyncio
async def test_get_forecast(weather_server, mock_forecast_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_forecast_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        result = await weather_server.get_forecast("London", 2)
        
        assert result["city"] == "London"
        assert len(result["forecasts"]) == 2
        assert result["forecasts"][0]["temperature"] == 22.5
        assert result["forecasts"][0]["description"] == "sunny"
        assert result["forecasts"][1]["temperature"] == 21.0
        assert result["forecasts"][1]["description"] == "partly cloudy"

@pytest.mark.asyncio
async def test_get_current_weather_error(weather_server):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("API Error")
        
        resource = await weather_server.get_current_weather({"city": "InvalidCity"})
        assert "API Error" in resource.error

@pytest.mark.asyncio
async def test_get_forecast_error(weather_server):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("API Error")
        
        result = await weather_server.get_forecast("InvalidCity", 2)
        assert "API Error" in result["error"]

def test_weather_server_initialization_without_api_key():
    os.environ.pop("OPENWEATHER_API_KEY", None)
    with pytest.raises(ValueError) as exc_info:
        WeatherServer()
    assert "OPENWEATHER_API_KEY environment variable is required" in str(exc_info.value) 

@pytest.mark.asyncio
async def test_rate_limiter():
    limiter = RateLimiter(calls=2, period=1)
    
    # First two calls should be allowed
    assert limiter.can_call()[0] is True
    assert limiter.can_call()[0] is True
    
    # Third call should be blocked
    can_call, wait_time = limiter.can_call()
    assert can_call is False
    assert wait_time > 0

@pytest.mark.asyncio
async def test_weather_caching(weather_server, mock_weather_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_weather_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        # First call should hit the API
        resource1 = await weather_server.get_current_weather({"city": "London"})
        assert resource1.metadata["cached"] is False
        
        # Second call should use cache
        resource2 = await weather_server.get_current_weather({"city": "London"})
        assert resource2.metadata["cached"] is True
        
        # Verify mock was called only once
        assert mock_get.call_count == 1

@pytest.mark.asyncio
async def test_forecast_caching(weather_server, mock_forecast_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_forecast_response
        mock_get.return_value.raise_for_status = MagicMock()
        
        # First call should hit the API
        result1 = await weather_server.get_forecast("London", 2)
        
        # Second call should use cache
        result2 = await weather_server.get_forecast("London", 2)
        
        # Verify mock was called only once
        assert mock_get.call_count == 1
        assert "generated_at" in result1
        assert result1 == result2

@pytest.mark.asyncio
async def test_api_timeout():
    server = WeatherServer()
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.Timeout("Connection timed out")
        
        with pytest.raises(requests.RequestException):
            await server.make_api_call("http://example.com", {})