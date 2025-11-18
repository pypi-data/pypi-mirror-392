import pytest
import asyncio
from asfeslib.net.http import HTTPClient


@pytest.mark.asyncio
async def test_http_get_json():
    async with HTTPClient(base_url="https://jsonplaceholder.typicode.com") as http:
        data = await http.get("/todos/1")
        assert isinstance(data, dict)
        assert data["id"] == 1


@pytest.mark.asyncio
async def test_http_404_handling():
    async with HTTPClient(base_url="https://jsonplaceholder.typicode.com") as http:
        res = await http.get("/nonexistent")
        assert res is None

@pytest.mark.asyncio
async def test_http_logs_strip_query_and_fragment(caplog):
    """
    Проверяем, что в логах не появляются query-параметры и фрагмент
    (например, токены ?token=SECRET).
    """
    class DummyResponse:
        def __init__(self):
            self.status = 200
            self.headers = {"Content-Type": "application/json"}

        async def json(self):
            return {"ok": True}

        async def text(self):
            return "ok"

        async def read(self):
            return b"ok"

        def raise_for_status(self):
            pass

    class DummyRequestCM:
        def __init__(self, resp):
            self._resp = resp

        async def __aenter__(self):
            return self._resp

        async def __aexit__(self, exc_type, exc, tb):
            pass

    class DummySession:
        def __init__(self, resp):
            self._resp = resp
            self.closed = False

        def request(self, *args, **kwargs):
            return DummyRequestCM(self._resp)

        async def close(self):
            self.closed = True

    http = HTTPClient(base_url="https://example.com")
    http.session = DummySession(DummyResponse())

    url = "/api/test?token=SECRET&x=1#frag"

    with caplog.at_level("DEBUG"):
        await http.get(url)

    messages = "\n".join(rec.getMessage() for rec in caplog.records)

    assert "SECRET" not in messages
    assert "token=" not in messages

    assert "https://example.com/api/test" in messages

@pytest.mark.asyncio
async def test_http_rejects_unsupported_schemes():
    http = HTTPClient()

    with pytest.raises(ValueError):
        await http.get("file:///etc/passwd")

    with pytest.raises(ValueError):
        await http.get("ftp://example.com/resource")

@pytest.mark.asyncio
async def test_http_relative_url_without_base_raises():
    http = HTTPClient()
    
    with pytest.raises(ValueError):
        await http.get("/api/test")