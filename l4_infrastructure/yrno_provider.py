import logging
from datetime import timedelta
from datetime import date
from l3_domain.weather_provider import WeatherProvider
from l4_infrastructure.file_cache import FileCache
from l4_infrastructure.http_client import HttpClient 
import config

logger = logging.getLogger(__name__)

class YrNoProvider(WeatherProvider):
    def __init__(self, cache: FileCache, http_client: HttpClient = None):
        self.cache = cache
        self.http = http_client or HttpClient()
        # Belgrade coordinates
        self.city_coords = {
            "Belgrade": (44.8176, 20.4569)
        }

    async def fetch_day(self, city: str, day: date) -> dict:        
        if self.cache.exists("YR.NO", city, day):
            logger.info("provider.yrno cache-hit city=%s day=%s", city, day)
            return self.cache.load("YR.NO", city, day)

        logger.info("provider.yrno fetch city=%s day=%s", city, day)

        lat, lon = self.city_coords.get(city, (None, None))
        if lat is None:
            raise ValueError(f"No coordinates for city {city}")

        url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
        
        data = await self.http.get(url)
        result = {"forecast": f"data for {day}", "raw": data}
        self.cache.save("YR.NO", city, day, result)
        return result

    async def fetch(self, city: str, start_day: date, days: int = config.FORECAST_DAYS):
        results = []
        for i in range(days):
            day = start_day + timedelta(days=i)
            day_data = await self.fetch_day(city, day)
            results.append(day_data)
        return results