from __future__ import annotations

from datetime import date
from typing import Protocol


class WeatherProvider(Protocol):
    async def fetch(self, city: str, start_day: date, days: int) -> list[dict]:
        """Fetch `days` of forecast data starting at `start_day`."""


class RawWeatherProvider(WeatherProvider, Protocol):
    provider_name: str

    async def fetch_raw(self, city: str) -> dict:
        """Fetch the raw upstream payload for `city`."""

    def extract_days(self, raw_data: dict, start_day: date, days: int) -> list[dict]:
        """Extract the requested day range from a raw upstream payload."""