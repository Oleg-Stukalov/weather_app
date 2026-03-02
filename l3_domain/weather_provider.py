from datetime import date


class WeatherProvider:
    async def fetch(self, city: str, day: date):
        """Fetch forecast for a city starting from start_day for given number of days."""
        return {"forecast": "dummy"}