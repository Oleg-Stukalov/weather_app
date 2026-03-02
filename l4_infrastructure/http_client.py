import asyncio 
import aiohttp
import config

class HttpClient:
    async def get(self, url: str):
        for attempt in range(config.HTTP_RETRIES):
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=config.HTTP_TIMEOUT)
                ) as session:
                    async with session.get(url, headers={"User-Agent": config.USER_AGENT}) as resp:
                        if resp.status != 200:
                            raise Exception(f"HTTP {resp.status}")
                        return await resp.json()
            except Exception:
                if attempt < config.HTTP_RETRIES - 1:
                    await asyncio.sleep(1)
                else:
                    raise