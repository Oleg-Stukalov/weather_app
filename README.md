# Weather_app

Weather_app is a demo asynchronous web application for fetching weather forecasts, featuring caching and extensible providers.

The application follows SOLID with separated layers:

- **l1_launcher** — backend endpoints  
- **l2_application** — business logic / UseCases (forecast retrieval, cache handling)  
- **l3_domain** — abstractions and interfaces (WeatherProvider)  
- **l4_infrastructure** — external services implementation (HTTP clients, cache, providers)  

## Features

- Multi-day forecasts for multiple cities (now Belgrade 14 d)  
- File system caching (`forecasts/`)  
- Extensible weather providers (now `YR.NO`)  
- Asynchronous HTTP requests with retries  
- Minimal test coverage  

## Technology stack

- Python 3.12  
- FastAPI + Uvicorn  
- Async HTTP: `aiohttp`, `httpx`  
- Testing: `pytest`, `pytest-asyncio`, `pytest-cov`  

## Configuration

All basic settings live in `config.py`:

- `FORECAST_DAYS` – how many days to fetch (default `14`)  
- `CACHE_DIR` – cache root directory (default `forecasts`)  
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
      "source": "CACHE | YR.NO",
      "data": { "...": "provider specific payload" }
    }
  ]
}
```

On first request for a given `(provider, city, day)` the app calls the upstream provider and stores the response in the file cache. Subsequent requests read from cache until the date changes.
