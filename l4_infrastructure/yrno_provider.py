import logging
from collections import defaultdict
from datetime import date, datetime
from datetime import timedelta

import config
from l3_domain.weather_provider import RawWeatherProvider
from l4_infrastructure.http_client import HttpClient

logger = logging.getLogger(__name__)


class YrNoProvider(RawWeatherProvider):
    provider_name = "YR.NO"

    def __init__(self, http_client: HttpClient = None):
        self.http = http_client or HttpClient()
        # Belgrade coordinates
        self.city_coords = {
            "Belgrade": (44.8176, 20.4569)
        }

    def _get_coordinates(self, city: str) -> tuple[float, float]:
        lat, lon = self.city_coords.get(city, (None, None))
        if lat is None:
            raise ValueError(f"No coordinates for city {city}")
        return lat, lon

    @staticmethod
    def _day_from_timestamp(timestamp: str) -> date:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date()

    def extract_days(self, raw_data: dict, start_day: date, days: int) -> list[dict]:
        timeseries = raw_data.get("properties", {}).get("timeseries", [])
        entries_by_day: dict[date, list[dict]] = defaultdict(list)

        for entry in timeseries:
            timestamp = entry.get("time")
            if not timestamp:
                continue
            entries_by_day[self._day_from_timestamp(timestamp)].append(entry)

        results = []
        for offset in range(days):
            current_day = start_day + timedelta(days=offset)
            day_entries = entries_by_day.get(current_day, [])
            if not day_entries:
                logger.warning("provider.yrno missing-timeseries city_day=%s", current_day)
            results.append({"day": current_day.isoformat(), "timeseries": day_entries})

        return results

    async def fetch_raw(self, city: str) -> dict:
        lat, lon = self._get_coordinates(city)
        url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
        logger.info("provider.yrno fetch_raw city=%s url=%s", city, url)
        return await self.http.get(url)

    async def fetch(self, city: str, start_day: date, days: int = config.FORECAST_DAYS):
        logger.info("provider.yrno fetch city=%s start_day=%s days=%s", city, start_day, days)
        raw_data = await self.fetch_raw(city)
        return self.extract_days(raw_data, start_day, days)