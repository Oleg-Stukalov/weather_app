import os
import time
from datetime import date

import pytest

from l4_infrastructure.cached_weather_provider import CachedWeatherProvider
from l4_infrastructure.file_cache import FileCache


class FakeInnerProvider:
    def __init__(self, raw_result: dict, extracted_result: list[dict]):
        self.provider_name = "FAKE"
        self.raw_result = raw_result
        self.extracted_result = extracted_result
        self.fetch_raw_called = None
        self.extract_called = None

    async def fetch_raw(self, city: str) -> dict:
        self.fetch_raw_called = city
        return self.raw_result

    def extract_days(self, raw_data: dict, start_day: date, days: int) -> list[dict]:
        self.extract_called = (raw_data, start_day, days)
        return self.extracted_result


@pytest.mark.asyncio
async def test_cached_weather_provider_uses_fresh_raw_cache_hit(tmp_path):
    start_day = date(2026, 3, 2)
    cache = FileCache(base_path=tmp_path)
    raw_payload = {"properties": {"timeseries": [{"time": "2026-03-02T00:00:00Z"}]}}
    expected = [{"day": "2026-03-02", "timeseries": [{"time": "2026-03-02T00:00:00Z"}]}]
    await cache.save_compact("FAKE", "Belgrade", raw_payload)

    inner = FakeInnerProvider(raw_result={"properties": {}}, extracted_result=expected)
    provider = CachedWeatherProvider(inner=inner, cache=cache)

    result = await provider.fetch("Belgrade", start_day, days=2)

    assert result == expected
    assert inner.fetch_raw_called is None
    assert inner.extract_called == (raw_payload, start_day, 2)
    assert provider.provider_name == "FAKE"


@pytest.mark.asyncio
async def test_cached_weather_provider_saves_raw_cache_on_miss(tmp_path):
    start_day = date(2026, 3, 2)
    cache = FileCache(base_path=tmp_path)
    raw_payload = {"properties": {"timeseries": [{"time": "2026-03-02T00:00:00Z"}]}}
    expected = [{"day": "2026-03-02", "timeseries": raw_payload["properties"]["timeseries"]}]
    inner = FakeInnerProvider(raw_result=raw_payload, extracted_result=expected)
    provider = CachedWeatherProvider(inner=inner, cache=cache)

    result = await provider.fetch("Belgrade", start_day, days=2)

    assert result == expected
    assert inner.fetch_raw_called == "Belgrade"
    assert await cache.load_compact("FAKE", "Belgrade") == raw_payload
    assert inner.extract_called == (raw_payload, start_day, 2)


@pytest.mark.asyncio
async def test_cached_weather_provider_refreshes_expired_raw_cache(tmp_path):
    start_day = date(2026, 3, 2)
    cache = FileCache(base_path=tmp_path)
    stale_payload = {"properties": {"timeseries": [{"time": "2026-03-01T00:00:00Z"}]}}
    fresh_payload = {"properties": {"timeseries": [{"time": "2026-03-02T00:00:00Z"}]}}
    expected = [{"day": "2026-03-02", "timeseries": fresh_payload["properties"]["timeseries"]}]
    await cache.save_compact("FAKE", "Belgrade", stale_payload)
    path = tmp_path / "FAKE" / "Belgrade" / "compact.json"
    stale_mtime = time.time() - 120
    os.utime(path, (stale_mtime, stale_mtime))

    inner = FakeInnerProvider(raw_result=fresh_payload, extracted_result=expected)
    provider = CachedWeatherProvider(inner=inner, cache=cache, ttl_seconds=60)

    result = await provider.fetch("Belgrade", start_day, days=1)

    assert result == expected
    assert inner.fetch_raw_called == "Belgrade"
    assert await cache.load_compact("FAKE", "Belgrade") == fresh_payload
    assert inner.extract_called == (fresh_payload, start_day, 1)
