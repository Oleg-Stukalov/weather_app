import pytest
from datetime import date, timedelta

from l2_application.get_forecast import GetForecastUseCase
from l2_application.schemas import ForecastResult


class FakeProvider:
    def __init__(self):
        self.called = None

    async def fetch(self, city: str, start_day: date, days: int):
        self.called = (city, start_day, days)
        return [
            {"forecast": f"data for {start_day + timedelta(days=i)}"}
            for i in range(days)
        ]


@pytest.mark.asyncio
async def test_usecase_maps_provider_forecast():
    provider = FakeProvider()
    usecase = GetForecastUseCase(provider=provider)

    forecast_days = 2
    result = await usecase.execute(city="Belgrade", days=forecast_days)

    assert isinstance(result, ForecastResult)
    assert len(result.days) == forecast_days
    assert provider.called[0] == "Belgrade"
    assert provider.called[2] == forecast_days
    assert all(day.source == "YR.NO" for day in result.days)