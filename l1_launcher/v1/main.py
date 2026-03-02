from fastapi import FastAPI, HTTPException, Query
import logging
import config
from l2_application.get_forecast import GetForecastUseCase
from l4_infrastructure.file_cache import FileCache
from l4_infrastructure.yrno_provider import YrNoProvider

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

app = FastAPI(title="Weather_forecast app")

def get_forecast_usecase() -> GetForecastUseCase:
    cache = FileCache(base_path=config.CACHE_DIR)
    provider = YrNoProvider(cache)
    return GetForecastUseCase(
        cache=cache, 
        provider=provider,
    )

@app.get("/forecast")
async def forecast(city: str = Query(..., description="City name for forecast")):
    usecase = get_forecast_usecase()
    try:
        result = await usecase.execute(city)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"days": [dict(day=d.day.isoformat(), source=d.source, data=d.data) for d in result.days]}