from datetime import date, timedelta
import logging
from l2_application.schemas import ForecastDay, ForecastResult
from l4_infrastructure.yrno_provider import YrNoProvider
from l4_infrastructure.file_cache import FileCache
from l4_infrastructure.http_client import HttpClient
import config

logger = logging.getLogger(__name__)


class GetForecastUseCase:
    def __init__(self, cache: FileCache = None, provider: YrNoProvider = None, http_client: HttpClient = None):
        self.cache = cache or FileCache(root_dir=config.CACHE_DIR)
        self.provider = provider or YrNoProvider(self.cache)

    async def execute(self, city: str, days: int = config.FORECAST_DAYS):
        start_day = date.today()
        days_list = []
        logger.info("usecase.get_forecast start city=%s days=%s start_day=%s", city, days, start_day)

        i = 0
        while i < days:
            day = start_day + timedelta(days=i)

            if self.cache.exists("YR.NO", city, day):
                logger.info("usecase.get_forecast cache-hit city=%s day=%s", city, day)
                data = self.cache.load("YR.NO", city, day)
                days_list.append(ForecastDay(day=day, source="CACHE", data=data))
                i += 1
            else:
                remaining_days = days - i
                logger.info(
                    "usecase.get_forecast cache-miss city=%s day=%s fetching_remaining_days=%s",
                    city,
                    day,
                    remaining_days,
                )
                raw = await self.provider.fetch(city, day, days=remaining_days)

                for offset in range(remaining_days):
                    current_day = day + timedelta(days=offset)
                    day_data = raw[offset]
                    days_list.append(
                        ForecastDay(day=current_day, source="YR.NO", data=day_data)
                    )
                    self.cache.save("YR.NO", city, current_day, day_data)

                break

        return ForecastResult(days=days_list)