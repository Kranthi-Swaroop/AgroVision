import aiohttp
from app.models.schemas import WeatherData


class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def get_weather(self, latitude: float, longitude: float) -> WeatherData:
        if not self.api_key or self.api_key == "demo_mode":
            return WeatherData(
                humidity=65,
                temperature=28.0,
                description="partly cloudy",
                wind_speed=3.5
            )
        
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric"
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=params, timeout=10) as response:
                    if response.status != 200:
                        return self._fallback_weather()
                    data = await response.json()
                    return WeatherData(
                        humidity=data["main"]["humidity"],
                        temperature=data["main"]["temp"],
                        description=data["weather"][0]["description"],
                        wind_speed=data["wind"]["speed"]
                    )
        except Exception:
            return self._fallback_weather()
    
    def _fallback_weather(self) -> WeatherData:
        return WeatherData(
            humidity=70,
            temperature=25.0,
            description="unknown",
            wind_speed=2.0
        )
