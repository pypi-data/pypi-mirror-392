"""
Клиент OpenSky Network (https://opensky-network.org/).

Это публичный анонимный API (без ключа, но с лимитами).
Задача — быстро получить live-трафик для учебных задач.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import httpx


def _validate_bbox(
    bbox: Tuple[float, float, float, float]
) -> Tuple[float, float, float, float]:
    """
    Валидация bbox: (min_lat, min_lon, max_lat, max_lon).
    Бросает ValueError при некорректных значениях.
    """
    min_lat, min_lon, max_lat, max_lon = bbox

    if not (-90.0 <= min_lat <= 90.0 and -90.0 <= max_lat <= 90.0):
        raise ValueError("Широта должна быть в диапазоне [-90, 90].")

    if not (-180.0 <= min_lon <= 180.0 and -180.0 <= max_lon <= 180.0):
        raise ValueError("Долгота должна быть в диапазоне [-180, 180].")

    if min_lat > max_lat or min_lon > max_lon:
        raise ValueError(
            "Ожидается min_lat <= max_lat и min_lon <= max_lon для bbox."
        )

    return min_lat, min_lon, max_lat, max_lon


def _is_state_seq(obj: Any, min_len: int) -> bool:
    """
    Проверка, что объект похож на state-запись OpenSky:
    последовательность (list/tuple) длиной минимум min_len.
    """
    return isinstance(obj, (list, tuple)) and len(obj) >= min_len


class OpenSkyClient:
    """
    Асинхронный клиент OpenSky.

    Примеры:

        async with OpenSkyClient() as client:
            states = await client.get_states(bbox=(50, 30, 60, 40))
    """

    BASE_URL = "https://opensky-network.org/api"

    def __init__(self, timeout: float = 10.0):
        self._timeout_value = float(timeout)
        self._client: Optional[httpx.AsyncClient] = None

    def _build_client(self) -> httpx.AsyncClient:
        """
        Внутренний конструктор httpx.AsyncClient с base_url, timeout и limits.
        """
        return httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=httpx.Timeout(self._timeout_value),
            limits=httpx.Limits(
                max_connections=50,
                max_keepalive_connections=10,
            ),
            headers={"User-Agent": "asfeslib-opensky-client"},
        )

    async def __aenter__(self) -> "OpenSkyClient":
        self._client = self._build_client()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client is not None:
            await self._client.aclose()
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """
        Ленивая инициализация клиента. Позволяет использовать OpenSkyClient
        без контекстного менеджера, но при этом не плодить клиентов.
        """
        if self._client is None:
            self._client = self._build_client()
        return self._client

    async def get_states(
        self,
        bbox: Optional[Tuple[float, float, float, float]] = None,
        icao24: Optional[str] = None,
        callsign: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Базовый вызов /states/all.

        Параметры:
          bbox     — кортеж (min_lat, min_lon, max_lat, max_lon)
          icao24   — фильтр по ICAO24 (нижний или верхний регистр)
          callsign — фильтр по позывному (частичное совпадение, без пробелов)

        Возвращает оригинальный JSON OpenSky (но с уже отфильтрованным
        полем "states", если заданы фильтры).
        """
        params: Dict[str, Any] = {}

        if bbox is not None:
            min_lat, min_lon, max_lat, max_lon = _validate_bbox(bbox)
            params["lamin"] = min_lat
            params["lomin"] = min_lon
            params["lamax"] = max_lat
            params["lomax"] = max_lon

        resp = await self.client.get(f"{self.BASE_URL}/states/all", params=params)
        resp.raise_for_status()

        data = resp.json() or {}
        if not isinstance(data, dict):
            raise ValueError("Неожиданная структура JSON от OpenSky API.")

        states_raw = data.get("states") or []
        if not isinstance(states_raw, list):
            try:
                states_raw = list(states_raw)
            except TypeError:
                states_raw = []

        states: List[Any] = states_raw

        if icao24 is not None:
            icao24_norm = icao24.strip().lower()
            filtered: List[Any] = []
            for s in states:
                if not _is_state_seq(s, 1):
                    continue
                v = s[0]
                if isinstance(v, str) and v.lower() == icao24_norm:
                    filtered.append(s)
            states = filtered

        if callsign is not None:
            cs_norm = callsign.strip().upper().replace(" ", "")
            filtered = []
            for s in states:
                if not _is_state_seq(s, 2):
                    continue
                v = s[1]
                if isinstance(v, str) and cs_norm in v.replace(" ", "").upper():
                    filtered.append(s)
            states = filtered

        data["states"] = states
        return data

    async def live_area(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
    ) -> List[Dict[str, Any]]:
        """
        Упрощённый метод: все борта в заданном прямоугольнике.

        Возвращает список словарей:
        {
            "icao24": str,
            "callsign": str | None,
            "country": str | None,
            "lat": float | None,
            "lon": float | None,
            "altitude_m": float | None,
            "velocity_mps": float | None,
            "heading_deg": float | None,
        }
        """
        raw = await self.get_states(bbox=(min_lat, min_lon, max_lat, max_lon))
        out: List[Dict[str, Any]] = []

        for s in raw.get("states") or []:
            try:
                state = {
                    "icao24": s[0],
                    "callsign": (s[1] or "").strip() or None,
                    "country": s[2],
                    "lon": s[5],
                    "lat": s[6],
                    "altitude_m": s[7],
                    "velocity_mps": s[9],
                    "heading_deg": s[10],
                }
                out.append(state)
            except Exception:
                continue

        return out

    async def by_icao24(self, icao24: str) -> List[Any]:
        """
        Все борта с заданным ICAO24 (обычно один).
        """
        raw = await self.get_states(icao24=icao24)
        return raw.get("states") or []

    async def by_callsign(self, callsign: str) -> List[Any]:
        """
        Поиск по позывному (callsign).
        """
        raw = await self.get_states(callsign=callsign)
        return raw.get("states") or []
