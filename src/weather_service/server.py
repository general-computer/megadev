from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass
import os
import time
import logging
from datetime import datetime, timedelta
import requests
from mcp import Server, Resource, Tool
from dotenv import load_dotenv
from cachetools import TTLCache

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    temperature: float
    description: str
    humidity: int
    wind_speed: float
    feels_like: float
    pressure: int
    clouds: int
    timestamp: datetime

class RateLimiter:
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.timestamps = []

    def can_call(self) -> Tuple[bool, float]:
        now = time.time()
        self.timestamps = [ts for ts in self.timestamps if now - ts < self.period]
        
        if len(self.timestamps) < self.calls:
            self.timestamps.append(now)
            return True, 0
        
        return False, self.period - (now - self.timestamps[0])

class WeatherServer(Server):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable is required")
        
        # Cache for weather data (30 minutes TTL)
        self.weather_cache = TTLCache(maxsize=100, ttl=1800)
        # Cache for forecast data (1 hour TTL)
        self.forecast_cache = TTLCache(maxsize=100, ttl=3600)
        # Rate limiter (60 calls per minute)
        self.rate_limiter = RateLimiter(calls=60, period=60)
        
        # Register resources
        self.register_resource("current_weather", self.get_current_weather)
        
        # Register tools
        self.register_tool(
            Tool(
                name="get_forecast",
                description="Get weather forecast for a specific city",
                parameters={
                    "city": {
                        "type": "string",
                        "description": "City name to get forecast for"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to forecast (1-5)",
                        "minimum": 1,
                        "maximum": 5
                    }
                },
                handler=self.get_forecast
            )
        )

    async def make_api_call(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make rate-limited API call"""
        can_call, wait_time = self.rate_limiter.can_call()
        
        if not can_call:
            logger.warning(f"Rate limit reached, waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API call failed: {str(e)}")
            raise

    def get_weather_data(self, city: str = "London") -> WeatherData:
        """Fetch current weather data from OpenWeatherMap API with caching"""
        cache_key = f"weather:{city.lower()}"
        
        if cache_key in self.weather_cache:
            logger.info(f"Cache hit for {city} weather data")
            return self.weather_cache[cache_key]
        
        logger.info(f"Fetching weather data for {city}")
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        data = self.make_api_call(url, params)
        
        weather_data = WeatherData(
            temperature=data["main"]["temp"],
            description=data["weather"][0]["description"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            feels_like=data["main"]["feels_like"],
            pressure=data["main"]["pressure"],
            clouds=data["clouds"]["all"],
            timestamp=datetime.fromtimestamp(data["dt"])
        )
        
        self.weather_cache[cache_key] = weather_data
        return weather_data

    async def get_current_weather(self, params: Optional[Dict[str, Any]] = None) -> Resource:
        """Resource handler for current weather"""
        try:
            city = params.get("city", "London") if params else "London"
            weather = self.get_weather_data(city)
            
            return Resource(
                data={
                    "temperature": weather.temperature,
                    "description": weather.description,
                    "humidity": weather.humidity,
                    "wind_speed": weather.wind_speed,
                    "feels_like": weather.feels_like,
                    "pressure": weather.pressure,
                    "clouds": weather.clouds,
                    "last_updated": weather.timestamp.isoformat()
                },
                metadata={
                    "city": city,
                    "unit": "metric",
                    "cached": city.lower() in self.weather_cache
                }
            )
        except Exception as e:
            logger.error(f"Error getting weather: {str(e)}")
            return Resource(error=str(e))

    async def get_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """Tool handler for weather forecast with caching"""
        cache_key = f"forecast:{city.lower()}:{days}"
        
        if cache_key in self.forecast_cache:
            logger.info(f"Cache hit for {city} forecast data")
            return self.forecast_cache[cache_key]
        
        logger.info(f"Fetching forecast data for {city}")
        url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "cnt": days * 8
        }
        
        try:
            data = self.make_api_call(url, params)
            
            daily_forecasts = []
            for i in range(0, len(data["list"]), 8):
                day_data = data["list"][i]
                forecast = {
                    "date": day_data["dt_txt"].split()[0],
                    "temperature": day_data["main"]["temp"],
                    "feels_like": day_data["main"]["feels_like"],
                    "description": day_data["weather"][0]["description"],
                    "humidity": day_data["main"]["humidity"],
                    "pressure": day_data["main"]["pressure"],
                    "wind_speed": day_data["wind"]["speed"],
                    "clouds": day_data["clouds"]["all"]
                }
                daily_forecasts.append(forecast)
            
            result = {
                "city": city,
                "forecasts": daily_forecasts,
                "generated_at": datetime.now().isoformat()
            }
            
            self.forecast_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Error getting forecast: {str(e)}")
            return {"error": str(e)} 