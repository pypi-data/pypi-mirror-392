import aiohttp
import asyncio
import logging
from typing import Optional, Any
from urllib.parse import urlsplit, urlunsplit

logger = logging.getLogger(__name__)


class HTTPClient:
    """
    Асинхронный HTTP-клиент на базе aiohttp.

    Поддерживает JSON, текст, бинарные ответы, ретраи и логирование.
    Важно:
    - поддерживаются только схемы http:// и https://;
    - в логах обрезаются query/fragment, чтобы не светить токены.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 10,
        max_retries: int = 2,
    ):
        self.base_url = self._normalize_base_url(base_url)
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None

    @staticmethod
    def _normalize_base_url(base_url: Optional[str]) -> str:
        if not base_url:
            return ""
        base_url = base_url.strip()
        if not base_url:
            return ""
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url должен начинаться с http:// или https://")
        return base_url.rstrip("/")

    @staticmethod
    def _build_url(base_url: str, url: str) -> str:
        url = url.strip()
        if url.startswith(("http://", "https://")):
            return url
        if "://" in url:
            raise ValueError(f"Неподдерживаемая схема в URL: {url!r}")
        if not base_url:
            raise ValueError("Нельзя использовать относительный URL без base_url")
        return f"{base_url}/{url.lstrip('/')}"

    @staticmethod
    def _safe_url_for_log(url: str) -> str:
        """
        Возвращает URL без query/fragment, чтобы не логировать токены и секреты.
        """
        try:
            parts = urlsplit(url)
            return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
        except Exception:
            return url

    async def _ensure_session(self) -> None:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Закрыть соединение."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        json: Any = None,
        data: Any = None,
        retry: Optional[int] = None,
        raise_on_fail: bool = False,
    ) -> Any:
        """
        Универсальный HTTP-запрос с retry, логированием и auto-decode ответа.

        Возвращает:
        - dict/list для JSON-ответов,
        - str для text/*,
        - bytes для всего остального,
        - None при ошибке/неуспехе (если raise_on_fail=False).
        """
        await self._ensure_session()
        assert self.session is not None

        full_url = self._build_url(self.base_url, url)
        log_url = self._safe_url_for_log(full_url)
        retries = retry if retry is not None else self.max_retries
        method_upper = method.upper()

        for attempt in range(1, retries + 1):
            try:
                async with self.session.request(
                    method=method_upper,
                    url=full_url,
                    params=params,
                    headers=headers,
                    json=json,
                    data=data,
                ) as response:
                    status = response.status
                    content_type = response.headers.get("Content-Type", "")

                    logger.debug(f"{method_upper} {log_url} → {status}")

                    if "application/json" in content_type:
                        result = await response.json()
                    elif "text" in content_type:
                        result = await response.text()
                    else:
                        result = await response.read()

                    if 200 <= status < 300:
                        return result

                    logger.warning(f"{method_upper} {log_url} вернул {status}")
                    if raise_on_fail:
                        response.raise_for_status()
                    return None

            except asyncio.TimeoutError:
                logger.error(f"Таймаут при запросе {method_upper} {log_url}")
            except aiohttp.ClientError as e:
                logger.error(f"Ошибка HTTP при запросе {method_upper} {log_url}: {e}")
            except Exception as e:
                logger.error(f"Неожиданная ошибка при запросе {method_upper} {log_url}: {e}")

            if attempt < retries:
                await asyncio.sleep(0.5 * attempt)
                logger.debug(f"🔁 Повтор {attempt}/{retries} для {method_upper} {log_url}")

        logger.error(f"Не удалось выполнить запрос {method_upper} {log_url} после {retries} попыток")
        return None

    async def get(self, url: str, **kwargs):
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs):
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs):
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs):
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs):
        return await self.request("DELETE", url, **kwargs)