import pytest
from l4_infrastructure.http_client import HttpClient

@pytest.mark.asyncio
async def test_http_client_get(monkeypatch):
    called = []

    class FakeResponse:
        status = 200
        async def json(self):
            return {"ok": True}
        async def __aenter__(self): 
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb): 
            pass

    class FakeSession:
        def __init__(self, *args, **kwargs): 
            pass        
        def get(self, url, headers=None):
            called.append(url)
            return FakeResponse()
        async def __aenter__(self): 
            return self        
        async def __aexit__(self, exc_type, exc_val, exc_tb): 
            pass

    monkeypatch.setattr("aiohttp.ClientSession", lambda *args, **kwargs: FakeSession())

    client = HttpClient()
    data = await client.get("https://example.com")
    assert data == {"ok": True}
    assert called[0] == "https://example.com"