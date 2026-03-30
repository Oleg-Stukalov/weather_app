import logging
from datetime import date

import config
from l3_domain.weather_provider import RawWeatherProvider
from l4_infrastructure.file_cache import FileCache

logger = logging.getLogger(__name__)


class CachedWeatherProvider(RawWeatherProvider):
    def __init__(
        self,
        inner: RawWeatherProvider,
        cache: FileCache,
        ttl_seconds: int = config.CACHE_TTL_SECONDS,
    ):
        self.inner = inner
        self.cache = cache
        self.ttl_seconds = ttl_seconds

    @property
    def provider_name(self) -> str:
        return self.inner.provider_name

    async def fetch(self, city: str, start_day: date, days: int) -> list[dict]:
        if await self.cache.has_fresh_compact(self.provider_name, city, self.ttl_seconds):
            logger.info("provider.cached hit provider=%s city=%s", self.provider_name, city)
            raw_data = await self.cache.load_compact(self.provider_name, city)
        else:
            logger.info("provider.cached miss provider=%s city=%s", self.provider_name, city)
            raw_data = await self.inner.fetch_raw(city)
            await self.cache.save_compact(self.provider_name, city, raw_data)

        return self.inner.extract_days(raw_data, start_day, days)

    async def fetch_raw(self, city: str) -> dict:
        return await self.inner.fetch_raw(city)

    def extract_days(self, raw_data: dict, start_day: date, days: int) -> list[dict]:
        return self.inner.extract_days(raw_data, start_day, days)
