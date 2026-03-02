import pytest
from datetime import date, timedelta

from l2_application.get_forecast import GetForecastUseCase
from l2_application.schemas import ForecastDay, ForecastResult


class FakeCache:
    def exists(self, provider: str, city: str, day: date) -> bool:
        return True # For all days say that cache is present

    def load(self, provider: str, city: str, day: date):
        return {"cached": True}


class FakeProvider:
    async def fetch(self, city: str, day: date):
        raise AssertionError("Provider should not be called when cache exists")


@pytest.mark.asyncio
async def test_usecase_returns_cached_forecast():
    cache = FakeCache()
    provider = FakeProvider()
    usecase = GetForecastUseCase(cache=cache, provider=provider)

    forecast_days = 2
    result = await usecase.execute(city="Belgrade", days=forecast_days)

    assert isinstance(result, ForecastResult)
    assert len(result.days) == forecast_days
    assert all(day.source == "CACHE" for day in result.days)