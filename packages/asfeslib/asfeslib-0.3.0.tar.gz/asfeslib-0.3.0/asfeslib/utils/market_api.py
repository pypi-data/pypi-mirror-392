"""
ASFESLIB: market_api — живые данные с бирж

Доступные источники:
- Binance        → криптовалюты (BTCUSDT, ETHUSDT и т.д.)
- Yahoo Finance  → акции (AAPL, TSLA, GOOGL) и ETF
- ExchangeRate   → мировые валюты (USD, EUR, RUB, GBP и т.д.)

ВНИМАНИЕ:
- Модуль асинхронный: функции safe_get / CryptoAPI / StocksAPI / ForexAPI / Market — awaitable.
"""

from __future__ import annotations

import asyncio
import time
from typing import Dict, Any, Optional

import requests
from urllib.parse import urlsplit, urlunsplit


_CACHE: Dict[str, Dict[str, Any]] = {}


class APIError(Exception):
    """Базовая ошибка удалённого API"""
    pass


class NotFoundError(APIError):
    """Инструмент/валюта не найдены на стороне провайдера"""
    pass


def _safe_url(url: str) -> str:
    """URL без query/fragment, чтобы не светить токены."""
    try:
        p = urlsplit(url)
        return urlunsplit((p.scheme, p.netloc, p.path, "", ""))
    except Exception:
        return url


async def safe_get(
    url: str,
    timeout: int = 5,
    retries: int = 3,
    retry_delay: float = 0.3,
    cache_ttl: Optional[int] = 60,
    use_cache: bool = True,
) -> Any:
    """
    Универсальный безопасный асинхронный GET-запрос с:
    - кэшем (cache_ttl секунд, можно отключить),
    - ретраями (retries попыток),
    - проверкой статуса.

    Важно:
    - не передавайте сюда URL напрямую от пользователя (иначе можно получить SSRF);
    - не кладите чувствительные данные (token, api_key) в query-строку — при ошибке
      URL попадает в текст исключения (но без query/fragment).
    """
    safe_url = _safe_url(url)

    now = time.time()

    if use_cache and cache_ttl and cache_ttl > 0:
        cache_entry = _CACHE.get(url)
        if cache_entry:
            age = now - cache_entry["timestamp"]
            if age < cache_ttl:
                return cache_entry["data"]

    last_exception: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            r = await asyncio.to_thread(requests.get, url, timeout=timeout)

            if r.status_code != 200:
                raise APIError(
                    f"API вернул ошибочный статус: {r.status_code}. URL: {safe_url}"
                )

            try:
                data = r.json()
            except Exception:
                raise APIError(
                    f"API вернул не-JSON ответ. URL: {safe_url}\nОтвет: {r.text[:200]}"
                )

            if use_cache and cache_ttl and cache_ttl > 0:
                _CACHE[url] = {
                    "timestamp": now,
                    "data": data,
                }

            return data

        except APIError:
            raise
        except Exception as e:
            last_exception = e
            if attempt < retries:
                await asyncio.sleep(retry_delay)

    raise APIError(f"Ошибка API после {retries} попыток: {last_exception}")


def clear_cache() -> None:
    """Полная очистка внутреннего кэша market_api"""
    _CACHE.clear()


class CryptoAPI:
    BASE = "https://api.binance.com"

    @staticmethod
    async def get_crypto_price(symbol: str) -> float:
        url = f"{CryptoAPI.BASE}/api/v3/ticker/price?symbol={symbol.upper()}"
        r = await safe_get(url, cache_ttl=3)
        try:
            return float(r["price"])
        except Exception:
            raise APIError(f"Некорректный ответ Binance для {symbol}: {r}")

    @staticmethod
    async def get_crypto_ohlc(symbol: str, interval: str = "1h", limit: int = 100):
        url = (
            f"{CryptoAPI.BASE}/api/v3/klines?"
            f"symbol={symbol.upper()}&interval={interval}&limit={limit}"
        )
        r = await safe_get(url, cache_ttl=10)

        try:
            return [
                {
                    "open_time": c[0],
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),
                    "volume": float(c[5]),
                }
                for c in r
            ]
        except Exception:
            raise APIError(f"Некорректный формат OHLC Binance для {symbol}: {r}")


class StocksAPI:
    BASE = "https://query1.finance.yahoo.com"

    @staticmethod
    def _extract_result(payload: dict, symbol: str) -> dict:
        """
        Аккуратно разбираем ответ Yahoo:
        - chart.error → ошибка провайдера
        - chart.result is None/[] → инструмент не найден
        """
        chart = payload.get("chart")
        if not chart:
            raise APIError(f"Некорректный ответ Yahoo Finance для {symbol}: нет поля 'chart'")

        error = chart.get("error")
        if error:
            code = error.get("code", "UNKNOWN")
            desc = error.get("description", "")
            raise APIError(f"Yahoo Finance error для {symbol}: {code} — {desc}")

        result = chart.get("result")
        if not result:
            raise NotFoundError(f"Инструмент {symbol} не найден в Yahoo Finance")

        return result[0]

    @staticmethod
    async def get_stock_price(symbol: str) -> float:
        url = f"{StocksAPI.BASE}/v8/finance/chart/{symbol}"
        r = await safe_get(url, cache_ttl=30)

        result = StocksAPI._extract_result(r, symbol)

        meta = result.get("meta") or {}
        if "regularMarketPrice" not in meta:
            raise APIError(
                f"В ответе Yahoo нет regularMarketPrice для {symbol}: {meta}"
            )

        return float(meta["regularMarketPrice"])

    @staticmethod
    async def get_stock_ohlc(symbol: str, interval: str = "1d", range_: str = "1mo"):
        url = (
            f"{StocksAPI.BASE}/v8/finance/chart/{symbol}"
            f"?interval={interval}&range={range_}"
        )
        r = await safe_get(url, cache_ttl=120)

        result = StocksAPI._extract_result(r, symbol)

        timestamps = result.get("timestamp") or []
        indicators_list = result.get("indicators", {}).get("quote") or []

        if not timestamps or not indicators_list:
            raise APIError(f"Некорректный OHLC ответ Yahoo для {symbol}: {result}")

        indicators = indicators_list[0]

        return [
            {
                "time": t,
                "open": indicators["open"][i],
                "high": indicators["high"][i],
                "low": indicators["low"][i],
                "close": indicators["close"][i],
                "volume": indicators["volume"][i],
            }
            for i, t in enumerate(timestamps)
        ]


class ForexAPI:
    BASE = "https://open.er-api.com/v6/latest/"

    @staticmethod
    async def get_forex_rate(base: str, quote: str) -> float:
        url = f"{ForexAPI.BASE}{base.upper()}"
        r = await safe_get(url, cache_ttl=3600)

        result = r.get("result")
        if result != "success":
            err_type = r.get("error-type", "unknown")
            raise APIError(
                f"Ошибка API Forex для {base.upper()}: result={result}, error-type={err_type}"
            )

        rates = r.get("rates") or {}
        q = quote.upper()
        if q not in rates:
            raise NotFoundError(
                f"Валюта {q} не найдена в ответе Forex для базовой {base.upper()}"
            )

        return float(rates[q])


class Market:
    """Удобный интерфейс ко всем API (асинхронный)."""

    @staticmethod
    async def crypto_price(symbol: str) -> float:
        return await CryptoAPI.get_crypto_price(symbol)

    @staticmethod
    async def crypto_ohlc(symbol: str, interval: str = "1h", limit: int = 100):
        return await CryptoAPI.get_crypto_ohlc(symbol, interval=interval, limit=limit)

    @staticmethod
    async def stock_price(symbol: str) -> float:
        return await StocksAPI.get_stock_price(symbol)

    @staticmethod
    async def stock_ohlc(symbol: str, interval: str = "1d", range_: str = "1mo"):
        return await StocksAPI.get_stock_ohlc(symbol, interval=interval, range_=range_)

    @staticmethod
    async def forex_rate(base: str, quote: str) -> float:
        return await ForexAPI.get_forex_rate(base, quote)
