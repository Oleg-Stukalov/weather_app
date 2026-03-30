from datetime import date, timedelta
import logging

import config
from l2_application.schemas import ForecastDay, ForecastResult
from l3_domain.weather_provider import WeatherProvider

logger = logging.getLogger(__name__)


class GetForecastUseCase:
    def __init__(self, provider: WeatherProvider | None = None):
        self.provider = provider

    async def execute(self, city: str, days: int = config.FORECAST_DAYS):
        if self.provider is None:
            raise ValueError("Weather provider is required")

        start_day = date.today()
        logger.info("usecase.get_forecast start city=%s days=%s start_day=%s", city, days, start_day)
        raw_days = await self.provider.fetch(city, start_day, days=days)
        days_list = []

        for offset, day_data in enumerate(raw_days):
            current_day = start_day + timedelta(days=offset)
            days_list.append(ForecastDay(day=current_day, source="YR.NO", data=day_data))

        return ForecastResult(days=days_list)