"""
Мини-база аэропортов и утилиты.

Это НЕ полный справочник, а лёгкий встроенный набор для примеров и
типичных задач. При желании можно заменить на загрузку из отдельного
JSON/БД.

Содержит несколько популярных аэропортов в разных частях мира.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, Tuple


AIRPORTS: Dict[str, Dict[str, Any]] = {
    "UUDD": {
        "icao": "UUDD",
        "iata": "DME",
        "name": "Moscow Domodedovo",
        "city": "Moscow",
        "country": "Russia",
        "lat": 55.408611,
        "lon": 37.906111,
        "elevation_m": 179.0,
        "timezone": "Europe/Moscow",
        "runways": [
            {"id": "14L/32R", "length_m": 3794, "surface": "Concrete"},
            {"id": "14R/32L", "length_m": 3500, "surface": "Concrete"},
        ],
    },
    "UUEE": {
        "icao": "UUEE",
        "iata": "SVO",
        "name": "Moscow Sheremetyevo",
        "city": "Moscow",
        "country": "Russia",
        "lat": 55.972599,
        "lon": 37.4146,
        "elevation_m": 192.0,
        "timezone": "Europe/Moscow",
        "runways": [
            {"id": "06L/24R", "length_m": 3700, "surface": "Concrete"},
            {"id": "06R/24L", "length_m": 3550, "surface": "Concrete"},
        ],
    },
    "UUWW": {
        "icao": "UUWW",
        "iata": "VKO",
        "name": "Moscow Vnukovo",
        "city": "Moscow",
        "country": "Russia",
        "lat": 55.5915,
        "lon": 37.2615,
        "elevation_m": 209.0,
        "timezone": "Europe/Moscow",
        "runways": [
            {"id": "01/19", "length_m": 3060, "surface": "Concrete"},
            {"id": "06/24", "length_m": 3060, "surface": "Concrete"},
        ],
    },
    "KLAX": {
        "icao": "KLAX",
        "iata": "LAX",
        "name": "Los Angeles International",
        "city": "Los Angeles",
        "country": "USA",
        "lat": 33.942791,
        "lon": -118.410042,
        "elevation_m": 38.0,
        "timezone": "America/Los_Angeles",
        "runways": [
            {"id": "06L/24R", "length_m": 3200, "surface": "Concrete"},
            {"id": "06R/24L", "length_m": 3200, "surface": "Concrete"},
            {"id": "07L/25R", "length_m": 3380, "surface": "Concrete"},
            {"id": "07R/25L", "length_m": 3380, "surface": "Concrete"},
        ],
    },
    "KJFK": {
        "icao": "KJFK",
        "iata": "JFK",
        "name": "New York John F. Kennedy",
        "city": "New York",
        "country": "USA",
        "lat": 40.641311,
        "lon": -73.778139,
        "elevation_m": 4.0,
        "timezone": "America/New_York",
        "runways": [
            {"id": "04L/22R", "length_m": 2560, "surface": "Asphalt"},
            {"id": "04R/22L", "length_m": 2560, "surface": "Asphalt"},
            {"id": "13L/31R", "length_m": 4423, "surface": "Asphalt"},
            {"id": "13R/31L", "length_m": 2560, "surface": "Asphalt"},
        ],
    },
}


def _normalize_code(code: str) -> str:
    return code.strip().upper()


def get_airport(code: str) -> Optional[Dict[str, Any]]:
    """
    Получить информацию об аэропорте по ICAO или IATA коду.

    Примеры:
        get_airport("UUDD")
        get_airport("dme")
        get_airport("LAX")
    """
    c = _normalize_code(code)

    if c in AIRPORTS:
        return AIRPORTS[c]

    for ap in AIRPORTS.values():
        if ap.get("iata", "").upper() == c:
            return ap

    return None


def airport_coords(code: str) -> Optional[Tuple[float, float]]:
    """
    Координаты (lat, lon) по коду.
    Возвращает None, если аэропорт не найден.
    """
    ap = get_airport(code)
    if not ap:
        return None
    return ap["lat"], ap["lon"]


def runway_length_m(code: str) -> Optional[int]:
    """
    Максимальная длина ВПП данного аэропорта (в метрах).
    Возвращает None, если данных нет.
    """
    ap = get_airport(code)
    if not ap:
        return None

    runways = ap.get("runways") or []
    if not runways:
        return None

    max_len = max((rw.get("length_m") or 0 for rw in runways), default=0)
    return max_len or None
