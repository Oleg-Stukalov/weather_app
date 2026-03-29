# Weather_app

Weather_app is a demo asynchronous web application for fetching weather forecasts, featuring caching and extensible providers.

The application follows SOLID with separated layers:

- **l1_api** — backend endpoints  
- **l2_application** — business logic / UseCases (forecast retrieval over provider abstractions)  
- **l3_domain** — abstractions and interfaces (WeatherProvider)  
- **l4_infrastructure** — external services implementation (HTTP clients, cache, providers)  

## Features

- Multi-day forecasts for multiple cities (now Belgrade 14 d)  
- File system caching of raw provider snapshots (`forecasts/`)  
- Extensible weather providers (now `YR.NO`)  
- Asynchronous HTTP requests with retries  
- Focused tests for provider, cache and endpoint behavior  

## Technology stack

- Python 3.12  
- FastAPI + Uvicorn  
- Async HTTP: `aiohttp`, `httpx`  
- Testing: `pytest`, `pytest-asyncio`, `pytest-cov`  

## Configuration

All basic settings live in `config.py`:

- `FORECAST_DAYS` – how many days to fetch (default `14`)  
- `CACHE_DIR` – cache root directory (default `forecasts`)  
- `CACHE_TTL_SECONDS` – freshness window for cached raw provider snapshots  
- `HTTP_RETRIES` / `HTTP_TIMEOUT` – retry count and total timeout for HTTP calls  
- `USER_AGENT` – sent to the upstream weather API  
- `LOG_LEVEL` – application log level (`INFO` by default, use `DEBUG` for more details)

## Installation & running locally

```bash
git clone <repo-url>
cd weather_app

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn l1_api.v1.main:app --port 8001
```

The service will be available at `http://localhost:8001`.

### API

#### `GET /forecast`

This is the main application endpoint. The app does not define `/`, so browser requests to `/` or `/favicon.ico` returning `404` are expected.

Query parameters:

- `city` – required, e.g. `Belgrade`

Example:

```bash
curl "http://localhost:8001/forecast?city=Belgrade"
```

Response shape:

```json
{
  "days": [
    {
      "day": "2026-03-02",
      "source": "YR.NO",
      "data": {
        "day": "2026-03-02",
        "timeseries": [ { "...": "provider specific payload" } ]
      }
    }
  ]
}
```

On first request for a given `(provider, city)` the app calls the upstream provider and stores the raw `compact` response in the file cache. Subsequent requests reuse that cached snapshot until the TTL expires, then refresh it with a new upstream call. Daily forecast items are derived from that cached raw snapshot in memory.
