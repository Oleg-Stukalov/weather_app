import pytest
from datetime import date, timedelta

from l2_application.get_forecast import GetForecastUseCase
from l2_application.schemas import ForecastDay, ForecastResult


class FakeCache:
    def exists(self, provider: str, city: str, day: date) -> bool:        
        return False # For all days say that cache is not present

    def load(self, provider: str, city: str, day: date):
        raise AssertionError("Cache.load should not be called when cache miss")

    def save(self, provider: str, city: str, day: date, data: dict):
        self.saved = getattr(self, "saved", [])
        self.saved.append((provider, city, day, data))

class FakeProvider:
    def __init__(self):
        self.called = []

    async def fetch(self, city: str, start_day: date, days: int):        
        self.called = [start_day + timedelta(days=i) for i in range(days)]
        return [{"forecast": f"data for {start_day + timedelta(days=i)}"} for i in range(days)]

@pytest.mark.asyncio
async def test_usecase_calls_provider_on_cache_miss():
    cache = FakeCache()
    provider = FakeProvider()
    usecase = GetForecastUseCase(cache=cache, provider=provider)

    result = await usecase.execute(city="Belgrade", days=2)
    print(provider.called)
    
    assert len(provider.called) == 2 # Check that provider was called for each day

    assert len(cache.saved) == 2 # Check that cache was updated

    assert isinstance(result, ForecastResult)
    assert all(isinstance(day, ForecastDay) for day in result.days)
    assert all(day.source == "YR.NO" for day in result.days)