import pytest
from fastapi.testclient import TestClient
from l1_launcher.v1.main import app

@pytest.mark.parametrize("city", ["Belgrade"])
def test_forecast_endpoint_sync(city):
    client = TestClient(app)
    
    response = client.get(f"/forecast?city={city}")
    
    assert response.status_code == 200
    data = response.json()
    assert "days" in data
    assert len(data["days"]) > 0
    for day in data["days"]:
        assert "day" in day
        assert "source" in day
        assert "data" in day