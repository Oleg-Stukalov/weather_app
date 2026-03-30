import pytest
from datetime import date

from l2_application.get_forecast import GetForecastUseCase


class FailingProvider:
    async def fetch(self, city: str, start_day: date, days: int):
        raise RuntimeError("Provider failed")


@pytest.mark.asyncio
async def test_usecase_propagates_provider_failure():
    provider = FailingProvider()
    usecase = GetForecastUseCase(provider=provider)

    with pytest.raises(RuntimeError, match="Provider failed"):
        await usecase.execute("Belgrade", days=2)