import pytest
from datetime import date
from l2_application.get_forecast import GetForecastUseCase
from l2_application.schemas import ForecastResult


class FakeCache:
    def exists(self, provider: str, city: str, day: date) -> bool:
        return True

    def load(self, provider: str, city: str, day: date) -> dict:
        return {"cached": True}

    def save(self, *args):
        raise AssertionError("Should not save when provider fails")


class FailingProvider:
    async def fetch(self, city: str, start_day: date, days: int):
        raise RuntimeError("Provider failed")


@pytest.mark.asyncio
async def test_fallback_to_cache_when_provider_fails():
    cache = FakeCache()
    provider = FailingProvider()
    usecase = GetForecastUseCase(cache=cache, provider=provider)

    result = await usecase.execute("Belgrade", days=2)

    assert isinstance(result, ForecastResult)
    assert all(day.source == "CACHE" for day in result.days)