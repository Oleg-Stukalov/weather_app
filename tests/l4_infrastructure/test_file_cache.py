from datetime import date

from l4_infrastructure.file_cache import FileCache


def test_file_cache_save_load_exists(tmp_path):
    cache = FileCache(base_path=tmp_path)

    provider = "YR.NO"
    city = "Belgrade"
    day = date(2026, 3, 2)

    data = {"temp": 15}

    assert not cache.exists(provider, city, day)

    cache.save(provider, city, day, data)

    assert cache.exists(provider, city, day)

   
    loaded = cache.load(provider, city, day)
    assert loaded == data