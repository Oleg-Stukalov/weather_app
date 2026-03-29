FORECAST_DAYS = 14
DEFAULT_CITIES = ["Belgrade"]  # optional preload

ENABLED_PROVIDERS = ["yrno"]

CACHE_DIR = "forecasts"
CACHE_TTL_SECONDS = 14400 # 4h

LOG_LEVEL = "INFO"

HTTP_RETRIES = 3 # 3 auto retries
HTTP_TIMEOUT = 30 # retry timeout in seconds

USER_AGENT = "Weather_app/0.1 contact@example.com"