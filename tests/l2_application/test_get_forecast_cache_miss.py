import pytest
from datetime import date, timedelta

from l2_application.get_forecast import GetForecastUseCase
from l2_application.schemas import ForecastDay, ForecastResult


class FakeProvider:
    def __init__(self):
        self.called = []

    async def fetch(self, city: str, start_day: date, days: int):
        self.called = [start_day + timedelta(days=i) for i in range(days)]
        return [{"forecast": f"data for {start_day + timedelta(days=i)}"} for i in range(days)]


@pytest.mark.asyncio
async def test_usecase_builds_consecutive_forecast_days():
    provider = FakeProvider()
    usecase = GetForecastUseCase(provider=provider)

    result = await usecase.execute(city="Belgrade", days=2)

    assert isinstance(result, ForecastResult)
    assert all(isinstance(day, ForecastDay) for day in result.days)
    assert all(day.source == "YR.NO" for day in result.days)
    assert len(provider.called) == 2
    assert result.days[1].day == result.days[0].day + timedelta(days=1)