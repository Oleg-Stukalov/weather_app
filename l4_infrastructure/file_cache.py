import asyncio
import json
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class FileCache:
    def __init__(self, base_path="forecasts"):
        self.base_path = Path(base_path)

    def _compact_path(self, provider: str, city: str) -> Path:
        return self.base_path / provider / city / "compact.json"

    def _has_fresh_compact_sync(self, provider: str, city: str, ttl_seconds: int) -> bool:
        path = self._compact_path(provider, city)
        if not path.exists():
            logger.debug("cache.compact provider=%s city=%s hit=%s", provider, city, False)
            return False

        age_seconds = time.time() - path.stat().st_mtime
        is_fresh = age_seconds <= ttl_seconds
        logger.debug(
            "cache.compact provider=%s city=%s age_seconds=%.2f ttl_seconds=%s fresh=%s",
            provider,
            city,
            age_seconds,
            ttl_seconds,
            is_fresh,
        )
        return is_fresh

    async def has_fresh_compact(self, provider: str, city: str, ttl_seconds: int) -> bool:
        return await asyncio.to_thread(self._has_fresh_compact_sync, provider, city, ttl_seconds)

    def _load_compact_sync(self, provider: str, city: str) -> dict:
        path = self._compact_path(provider, city)
        logger.info("cache.load_compact provider=%s city=%s path=%s", provider, city, path)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def load_compact(self, provider: str, city: str) -> dict:
        return await asyncio.to_thread(self._load_compact_sync, provider, city)

    def _save_compact_sync(self, provider: str, city: str, data: dict) -> None:
        path = self._compact_path(provider, city)
        logger.info("cache.save_compact provider=%s city=%s path=%s", provider, city, path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    async def save_compact(self, provider: str, city: str, data: dict) -> None:
        await asyncio.to_thread(self._save_compact_sync, provider, city, data)