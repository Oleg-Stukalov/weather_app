import json
from pathlib import Path
from datetime import date
import logging

logger = logging.getLogger(__name__)


class FileCache:
    def __init__(self, base_path="forecasts"):
        self.base_path = Path(base_path)

    def _day_path(self, provider: str, city: str, day: date):
        return self.base_path / provider / city / f"{day}.json"

    def exists(self, provider, city, day):
        path = self._day_path(provider, city, day)
        hit = path.exists()
        logger.debug("cache.exists provider=%s city=%s day=%s hit=%s", provider, city, day, hit)
        return hit

    def load(self, provider, city, day):
        path = self._day_path(provider, city, day)
        logger.info("cache.load provider=%s city=%s day=%s path=%s", provider, city, day, path)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, provider, city, day, data):
        path = self._day_path(provider, city, day)
        logger.info("cache.save provider=%s city=%s day=%s path=%s", provider, city, day, path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)