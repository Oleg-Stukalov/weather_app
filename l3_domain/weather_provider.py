from __future__ import annotations

from datetime import date
from typing import Protocol


class WeatherProvider(Protocol):
    async def fetch(self, city: str, start_day: date, days: int) -> list[dict]:
        """Fetch `days` of forecast data starting at `start_day`."""