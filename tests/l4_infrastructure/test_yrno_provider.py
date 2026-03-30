from datetime import date

import pytest

from l4_infrastructure.yrno_provider import YrNoProvider


class FakeHttpClient:
    def __init__(self, response: dict):
        self.response = response
        self.called_urls: list[str] = []

    async def get(self, url: str) -> dict:
        self.called_urls.append(url)
        return self.response


@pytest.mark.asyncio
async def test_yrno_provider_fetch_uses_single_http_call_for_multiple_days():
    response = {
        "properties": {
            "timeseries": [
                {"time": "2026-03-02T00:00:00Z", "data": {"instant": {"details": {"air_temperature": 11}}}},
                {"time": "2026-03-02T06:00:00Z", "data": {"instant": {"details": {"air_temperature": 13}}}},
                {"time": "2026-03-03T00:00:00Z", "data": {"instant": {"details": {"air_temperature": 10}}}},
                {"time": "2026-03-03T12:00:00Z", "data": {"instant": {"details": {"air_temperature": 15}}}},
                {"time": "2026-03-04T00:00:00Z", "data": {"instant": {"details": {"air_temperature": 9}}}},
            ]
        }
    }
    http = FakeHttpClient(response=response)
    provider = YrNoProvider(http_client=http)

    result = await provider.fetch("Belgrade", date(2026, 3, 2), days=2)

    assert len(http.called_urls) == 1
    assert http.called_urls[0] == (
        "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=44.8176&lon=20.4569"
    )
    assert result == [
        {
            "day": "2026-03-02",
            "timeseries": response["properties"]["timeseries"][:2],
        },
        {
            "day": "2026-03-03",
            "timeseries": response["properties"]["timeseries"][2:4],
        },
    ]


@pytest.mark.asyncio
async def test_yrno_provider_fetch_returns_empty_timeseries_when_day_missing():
    response = {
        "properties": {
            "timeseries": [
                {"time": "2026-03-02T00:00:00Z", "data": {"instant": {"details": {"air_temperature": 11}}}},
            ]
        }
    }
    http = FakeHttpClient(response=response)
    provider = YrNoProvider(http_client=http)

    result = await provider.fetch("Belgrade", date(2026, 3, 2), days=2)

    assert len(http.called_urls) == 1
    assert result == [
        {
            "day": "2026-03-02",
            "timeseries": response["properties"]["timeseries"],
        },
        {
            "day": "2026-03-03",
            "timeseries": [],
        },
    ]
