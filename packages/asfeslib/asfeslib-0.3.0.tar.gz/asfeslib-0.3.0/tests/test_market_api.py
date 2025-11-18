import pytest
import requests

import asfeslib.utils.market_api as market_api
from asfeslib.utils.market_api import (
    safe_get,
    clear_cache,
    APIError,
    NotFoundError,
    CryptoAPI,
    StocksAPI,
    ForexAPI,
    Market,
)


@pytest.fixture(autouse=True)
def _reset_cache():
    clear_cache()
    yield
    clear_cache()


class DummyResp:
    """Простой фейковый ответ requests.get для тестов"""

    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def json(self):
        if self._json_data is None:
            raise ValueError("No JSON")
        return self._json_data


@pytest.mark.asyncio
async def test_safe_get_uses_cache(monkeypatch):
    """Второй вызов с тем же URL и TTL должен брать из кэша"""

    calls = {"count": 0}

    def fake_get(url, timeout=5):
        calls["count"] += 1
        return DummyResp(json_data={"value": 123})

    monkeypatch.setattr(market_api.requests, "get", fake_get)

    url = "https://example.com/data"
    r1 = await safe_get(url, cache_ttl=60)
    r2 = await safe_get(url, cache_ttl=60)

    assert r1 == {"value": 123}
    assert r2 == {"value": 123}
    assert calls["count"] == 1


@pytest.mark.asyncio
async def test_safe_get_cache_disabled_with_use_cache_false(monkeypatch):
    """Если use_cache=False — кэш не используется вообще"""

    calls = {"count": 0}

    def fake_get(url, timeout=5):
        calls["count"] += 1
        return DummyResp(json_data={"value": 321})

    monkeypatch.setattr(market_api.requests, "get", fake_get)

    url = "https://example.com/no-cache"
    r1 = await safe_get(url, cache_ttl=60, use_cache=False)
    r2 = await safe_get(url, cache_ttl=60, use_cache=False)

    assert r1 == {"value": 321}
    assert r2 == {"value": 321}
    assert calls["count"] == 2


@pytest.mark.asyncio
async def test_safe_get_cache_ttl_expired(monkeypatch):
    """Если TTL истёк — запрос должен пойти снова и обновить timestamp"""

    times = [1000.0, 1100.0]

    def fake_time():
        return times.pop(0)

    def fake_get(url, timeout=5):
        return DummyResp(json_data={"value": 42})

    monkeypatch.setattr(market_api, "time", market_api.time)
    monkeypatch.setattr(market_api.time, "time", fake_time)
    monkeypatch.setattr(market_api.requests, "get", fake_get)

    url = "https://example.com/ttl"

    r1 = await safe_get(url, cache_ttl=50)
    r2 = await safe_get(url, cache_ttl=50)
    assert r1 == {"value": 42}
    assert r2 == {"value": 42}
    assert url in market_api._CACHE
    assert market_api._CACHE[url]["timestamp"] == 1100.0


@pytest.mark.asyncio
async def test_safe_get_non_200_raises_apierror(monkeypatch):
    """Нестатус 200 → APIError без повторов"""

    def fake_get(url, timeout=5):
        return DummyResp(status_code=500, json_data={"error": "fail"}, text="fail")

    monkeypatch.setattr(market_api.requests, "get", fake_get)

    with pytest.raises(APIError) as exc:
        await safe_get("https://example.com/error", cache_ttl=0)

    assert "500" in str(exc.value)


@pytest.mark.asyncio
async def test_safe_get_non_json_raises_apierror(monkeypatch):
    """Если .json() падает — APIError с обрезанным текстом ответа"""

    def fake_get(url, timeout=5):
        return DummyResp(status_code=200, json_data=None, text="NOT JSON RESPONSE")

    monkeypatch.setattr(market_api.requests, "get", fake_get)

    with pytest.raises(APIError) as exc:
        await safe_get("https://example.com/not-json", cache_ttl=0)

    assert "не-JSON" in str(exc.value)


@pytest.mark.asyncio
async def test_safe_get_network_error_retries_and_raises(monkeypatch):
    """Сетевые ошибки → несколько попыток и итоговый APIError"""

    calls = {"count": 0}

    def fake_get(url, timeout=5):
        calls["count"] += 1
        raise requests.exceptions.ConnectionError("boom")

    monkeypatch.setattr(market_api.requests, "get", fake_get)

    with pytest.raises(APIError) as exc:
        await safe_get("https://example.com/retry", retries=3, cache_ttl=0)

    assert "3 попыток" in str(exc.value)
    assert calls["count"] == 3


@pytest.mark.asyncio
async def test_clear_cache_empties_internal_cache(monkeypatch):
    """clear_cache должен реально очищать _CACHE"""

    def fake_get(url, timeout=5):
        return DummyResp(json_data={"x": 1})

    monkeypatch.setattr(market_api.requests, "get", fake_get)

    url = "https://example.com/cache"
    await safe_get(url, cache_ttl=60)

    assert url in market_api._CACHE

    clear_cache()
    assert market_api._CACHE == {}


@pytest.mark.asyncio
async def test_cryptoapi_get_crypto_price(monkeypatch):
    """CryptoAPI.get_crypto_price использует safe_get и возвращает float"""

    async def fake_safe_get(url, timeout=5, retries=3, retry_delay=0.3, cache_ttl=3, use_cache=True):
        return {"price": "123.45"}

    monkeypatch.setattr(market_api, "safe_get", fake_safe_get)

    price = await CryptoAPI.get_crypto_price("BTCUSDT")
    assert isinstance(price, float)
    assert price == pytest.approx(123.45)


@pytest.mark.asyncio
async def test_cryptoapi_get_crypto_ohlc(monkeypatch):
    """CryptoAPI.get_crypto_ohlc корректно парсит список свечей"""

    async def fake_safe_get(url, timeout=5, retries=3, retry_delay=0.3, cache_ttl=10, use_cache=True):
        return [
            [1, "1.0", "2.0", "0.5", "1.5", "10"],
            [2, "1.5", "2.5", "1.0", "2.0", "20"],
        ]

    monkeypatch.setattr(market_api, "safe_get", fake_safe_get)

    candles = await CryptoAPI.get_crypto_ohlc("BTCUSDT", interval="1h", limit=2)
    assert len(candles) == 2
    c0 = candles[0]
    assert c0["open_time"] == 1
    assert c0["open"] == pytest.approx(1.0)
    assert c0["high"] == pytest.approx(2.0)
    assert c0["low"] == pytest.approx(0.5)
    assert c0["close"] == pytest.approx(1.5)
    assert c0["volume"] == pytest.approx(10.0)


def test_stocksapi_extract_result_not_found():
    """_extract_result: пустой result → NotFoundError"""

    payload = {"chart": {"result": []}}
    with pytest.raises(NotFoundError):
        StocksAPI._extract_result(payload, "FAKE")


def test_stocksapi_extract_result_provider_error():
    """_extract_result: chart.error → APIError"""

    payload = {
        "chart": {
            "error": {
                "code": "Not Found",
                "description": "No data found",
            }
        }
    }
    with pytest.raises(APIError) as exc:
        StocksAPI._extract_result(payload, "FAKE")

    assert "Yahoo Finance error" in str(exc.value)


def test_stocksapi_extract_result_ok():
    """_extract_result: валидный ответ → возвращаем первый result"""

    payload = {
        "chart": {
            "result": [
                {"meta": {"symbol": "AAPL"}}
            ]
        }
    }
    result = StocksAPI._extract_result(payload, "AAPL")
    assert result["meta"]["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_stocksapi_get_stock_price_ok(monkeypatch):
    """get_stock_price: happy-path с regularMarketPrice"""

    async def fake_safe_get(url, timeout=5, retries=3, retry_delay=0.3, cache_ttl=30, use_cache=True):
        return {
            "chart": {
                "result": [
                    {"meta": {"regularMarketPrice": 150.5}}
                ],
                "error": None,
            }
        }

    monkeypatch.setattr(market_api, "safe_get", fake_safe_get)

    price = await StocksAPI.get_stock_price("AAPL")
    assert price == pytest.approx(150.5)


@pytest.mark.asyncio
async def test_stocksapi_get_stock_price_missing_price(monkeypatch):
    """get_stock_price: meta без regularMarketPrice → APIError"""

    async def fake_safe_get(url, timeout=5, retries=3, retry_delay=0.3, cache_ttl=30, use_cache=True):
        return {
            "chart": {
                "result": [
                    {"meta": {}}
                ],
                "error": None,
            }
        }

    monkeypatch.setattr(market_api, "safe_get", fake_safe_get)

    with pytest.raises(APIError):
        await StocksAPI.get_stock_price("AAPL")


@pytest.mark.asyncio
async def test_stocksapi_get_stock_ohlc_ok(monkeypatch):
    """get_stock_ohlc: корректный парсинг OHLC"""

    async def fake_safe_get(url, timeout=5, retries=3, retry_delay=0.3, cache_ttl=120, use_cache=True):
        return {
            "chart": {
                "result": [
                    {
                        "timestamp": [100, 200],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [1.0, 2.0],
                                    "high": [1.5, 2.5],
                                    "low": [0.5, 1.5],
                                    "close": [1.2, 2.2],
                                    "volume": [1000, 2000],
                                }
                            ]
                        },
                    }
                ],
                "error": None,
            }
        }

    monkeypatch.setattr(market_api, "safe_get", fake_safe_get)

    ohlc = await StocksAPI.get_stock_ohlc("AAPL", interval="1d", range_="1mo")
    assert len(ohlc) == 2
    first = ohlc[0]
    assert first["time"] == 100
    assert first["open"] == 1.0
    assert first["high"] == 1.5
    assert first["low"] == 0.5
    assert first["close"] == 1.2
    assert first["volume"] == 1000


@pytest.mark.asyncio
async def test_forexapi_get_forex_rate_ok(monkeypatch):
    """get_forex_rate: успешный ответ с курсом"""

    async def fake_safe_get(url, timeout=5, retries=3, retry_delay=0.3, cache_ttl=3600, use_cache=True):
        return {
            "result": "success",
            "rates": {
                "USD": 1.2345,
                "EUR": 0.9876,
            },
        }

    monkeypatch.setattr(market_api, "safe_get", fake_safe_get)

    rate = await ForexAPI.get_forex_rate("EUR", "USD")
    assert rate == pytest.approx(1.2345)


@pytest.mark.asyncio
async def test_forexapi_get_forex_rate_error_result(monkeypatch):
    """get_forex_rate: result != success → APIError"""

    async def fake_safe_get(url, timeout=5, retries=3, retry_delay=0.3, cache_ttl=3600, use_cache=True):
        return {
            "result": "error",
            "error-type": "invalid-key",
        }

    monkeypatch.setattr(market_api, "safe_get", fake_safe_get)

    with pytest.raises(APIError) as exc:
        await ForexAPI.get_forex_rate("EUR", "USD")

    assert "invalid-key" in str(exc.value)


@pytest.mark.asyncio
async def test_forexapi_get_forex_rate_not_found(monkeypatch):
    """get_forex_rate: нужной валюты нет в rates → NotFoundError"""

    async def fake_safe_get(url, timeout=5, retries=3, retry_delay=0.3, cache_ttl=3600, use_cache=True):
        return {
            "result": "success",
            "rates": {
                "EUR": 0.99,
            },
        }

    monkeypatch.setattr(market_api, "safe_get", fake_safe_get)

    with pytest.raises(NotFoundError):
        await ForexAPI.get_forex_rate("USD", "JPY")


@pytest.mark.asyncio
async def test_market_crypto_price_delegates_to_cryptoapi(monkeypatch):
    """Market.crypto_price должен делегировать в CryptoAPI.get_crypto_price"""

    called = {"args": None}

    async def fake_get_crypto_price(symbol: str) -> float:
        called["args"] = symbol
        return 999.0

    monkeypatch.setattr(market_api.CryptoAPI, "get_crypto_price", fake_get_crypto_price)

    value = await Market.crypto_price("BTCUSDT")
    assert value == 999.0
    assert called["args"] == "BTCUSDT"


@pytest.mark.asyncio
async def test_market_stock_price_delegates_to_stocksapi(monkeypatch):
    """Market.stock_price → StocksAPI.get_stock_price"""

    called = {"args": None}

    async def fake_get_stock_price(symbol: str) -> float:
        called["args"] = symbol
        return 123.0

    monkeypatch.setattr(market_api.StocksAPI, "get_stock_price", fake_get_stock_price)

    value = await Market.stock_price("AAPL")
    assert value == 123.0
    assert called["args"] == "AAPL"


@pytest.mark.asyncio
async def test_market_forex_rate_delegates_to_forexapi(monkeypatch):
    """Market.forex_rate → ForexAPI.get_forex_rate"""

    called = {"args": None}

    async def fake_get_forex_rate(base: str, quote: str) -> float:
        called["args"] = (base, quote)
        return 1.5

    monkeypatch.setattr(market_api.ForexAPI, "get_forex_rate", fake_get_forex_rate)

    value = await Market.forex_rate("EUR", "USD")
    assert value == 1.5
    assert called["args"] == ("EUR", "USD")