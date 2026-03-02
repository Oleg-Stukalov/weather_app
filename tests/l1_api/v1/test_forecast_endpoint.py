import pytest
from httpx import AsyncClient, ASGITransport
from l1_launcher.v1.main import app
from l2_application.schemas import ForecastDay, ForecastResult
from datetime import date

@pytest.mark.asyncio
async def test_forecast_endpoint_returns_200(monkeypatch):    
    class FakeUseCase:
        async def execute(self, city):
            days = [ForecastDay(day=date.today(), source="YR.NO", data={"forecast": "sunny"})]
            return ForecastResult(days=days)
   
    monkeypatch.setattr("l1_launcher.v1.main.get_forecast_usecase", lambda: FakeUseCase())

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/forecast?city=Belgrade")

    assert response.status_code == 200
    data = response.json()
    assert "days" in data
    assert len(data["days"]) == 1
    assert data["days"][0]["source"] == "YR.NO"