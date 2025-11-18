import pytest

from asfeslib.utils.market_api import (
    CryptoAPI,
    StocksAPI,
    ForexAPI,
    Market,
    APIError,
    NotFoundError,
)

pytestmark = pytest.mark.live


def _skip_if_yahoo_rate_limited(exc: APIError) -> None:
    """
    Если Yahoo вернул 429 (rate limit) — пропускаем тест.
    Иначе пробрасываем ошибку дальше.
    """
    msg = str(exc)
    if "429" in msg:
        pytest.skip("Yahoo Finance вернул HTTP 429 (rate limit) — пропускаем live-тест.")
    raise exc


@pytest.mark.asyncio
async def test_live_crypto_price_btcusdt():
    """Простая проверка: Binance отдаёт цену BTCUSDT > 0."""
    price = await CryptoAPI.get_crypto_price("BTCUSDT")
    assert isinstance(price, float)
    assert price > 0.0


@pytest.mark.asyncio
async def test_live_crypto_ohlc_btcusdt():
    """Проверка, что Binance отдаёт свечи и структура валидна."""
    candles = await CryptoAPI.get_crypto_ohlc("BTCUSDT", interval="1h", limit=10)
    assert isinstance(candles, list)
    assert len(candles) > 0

    c0 = candles[0]
    for key in ("open_time", "open", "high", "low", "close", "volume"):
        assert key in c0


@pytest.mark.asyncio
async def test_live_stock_price_aapl():
    """Yahoo Finance: реальная цена AAPL > 0."""
    try:
        price = await StocksAPI.get_stock_price("AAPL")
    except APIError as exc:
        _skip_if_yahoo_rate_limited(exc)
        raise
    else:
        assert isinstance(price, float)
        assert price > 0.0


@pytest.mark.asyncio
async def test_live_stock_ohlc_aapl():
    """Yahoo Finance: OHLC по AAPL имеет валидную структуру."""
    try:
        ohlc = await StocksAPI.get_stock_ohlc("AAPL", interval="1d", range_="1mo")
    except APIError as exc:
        _skip_if_yahoo_rate_limited(exc)
        raise
    else:
        assert isinstance(ohlc, list)
        assert len(ohlc) > 0

        first = ohlc[0]
        for key in ("time", "open", "high", "low", "close", "volume"):
            assert key in first


@pytest.mark.asyncio
async def test_live_stock_not_found_raises_notfounderror():
    """
    Невалидный тикер в Yahoo должен привести к NotFoundError.
    Если Yahoo отвечает 429 — тест скипается.
    """
    fake_symbol = "ASFESLIB_FAKE_TICKER_123456"

    try:
        await StocksAPI.get_stock_price(fake_symbol)
    except NotFoundError:
        return
    except APIError as exc:
        _skip_if_yahoo_rate_limited(exc)
        raise
    else:
        pytest.fail("Ожидали NotFoundError для несуществующего тикера, но исключения не было.")


@pytest.mark.asyncio
async def test_live_forex_rate_usd_eur():
    """ER-API: курс USD→EUR > 0."""
    rate = await ForexAPI.get_forex_rate("USD", "EUR")
    assert isinstance(rate, float)
    assert rate > 0.0


@pytest.mark.asyncio
async def test_live_forex_rate_not_found():
    """
    Невалидная котируемая валюта должна вызвать NotFoundError.
    Здесь ратлимит обычно не прилетает, но если что — тоже будет APIError.
    """
    with pytest.raises(NotFoundError):
        await ForexAPI.get_forex_rate("USD", "XXX_FAKE_CURRENCY")


@pytest.mark.asyncio
async def test_live_market_wrappers_crypto():
    """Проверка, что Market.* реально ходит в API и даёт адекватные значения (крипта)."""
    price = await Market.crypto_price("BTCUSDT")
    assert isinstance(price, float)
    assert price > 0.0

    candles = await Market.crypto_ohlc("BTCUSDT", interval="1h", limit=5)
    assert len(candles) > 0


@pytest.mark.asyncio
async def test_live_market_wrappers_stocks():
    """Проверка Market.* для акций (с учётом возможного 429 от Yahoo)."""
    try:
        price = await Market.stock_price("AAPL")
    except APIError as exc:
        _skip_if_yahoo_rate_limited(exc)
        raise
    else:
        assert isinstance(price, float)
        assert price > 0.0

    try:
        ohlc = await Market.stock_ohlc("AAPL", interval="1d", range_="1mo")
    except APIError as exc:
        _skip_if_yahoo_rate_limited(exc)
        raise
    else:
        assert isinstance(ohlc, list)
        assert len(ohlc) > 0