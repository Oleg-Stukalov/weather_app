import os
import time

import pytest

from l4_infrastructure.file_cache import FileCache


@pytest.mark.asyncio
async def test_file_cache_save_load_compact(tmp_path):
    cache = FileCache(base_path=tmp_path)

    provider = "YR.NO"
    city = "Belgrade"
    data = {"properties": {"timeseries": [{"time": "2026-03-02T00:00:00Z"}]}}

    assert not await cache.has_fresh_compact(provider, city, ttl_seconds=60)

    await cache.save_compact(provider, city, data)

    assert await cache.has_fresh_compact(provider, city, ttl_seconds=60)

    loaded = await cache.load_compact(provider, city)
    assert loaded == data


@pytest.mark.asyncio
async def test_file_cache_compact_expires_by_ttl(tmp_path):
    cache = FileCache(base_path=tmp_path)
    provider = "YR.NO"
    city = "Belgrade"
    data = {"properties": {"timeseries": []}}

    await cache.save_compact(provider, city, data)
    path = tmp_path / provider / city / "compact.json"
    stale_mtime = time.time() - 120
    os.utime(path, (stale_mtime, stale_mtime))

    assert not await cache.has_fresh_compact(provider, city, ttl_seconds=60)