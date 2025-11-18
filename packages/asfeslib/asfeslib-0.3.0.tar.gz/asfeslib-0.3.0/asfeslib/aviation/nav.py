"""
Навигация и геодезия для авиации.

Содержит:
- расстояние (Haversine),
- начальный курс,
- точка назначения,
- ETA,
- учёт ветра.
"""

from __future__ import annotations

from math import radians, degrees, sin, cos, atan2, asin
from typing import Tuple


EARTH_RADIUS_KM = 6371.0


def haversine_distance_km(
    lat1_deg: float,
    lon1_deg: float,
    lat2_deg: float,
    lon2_deg: float,
) -> float:
    """
    Расстояние между двумя точками по сфере (Haversine).
    Возвращает расстояние в км.

    Дополнительно защищаемся от fp-ошибок, поджимая аргумент asin в [0, 1].
    """
    lat1 = radians(lat1_deg)
    lon1 = radians(lon1_deg)
    lat2 = radians(lat2_deg)
    lon2 = radians(lon2_deg)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    if a < 0.0:
        a = 0.0
    elif a > 1.0:
        a = 1.0

    c = 2 * asin(a ** 0.5)
    return EARTH_RADIUS_KM * c




def initial_bearing_deg(
    lat1_deg: float,
    lon1_deg: float,
    lat2_deg: float,
    lon2_deg: float,
) -> float:
    """
    Начальный курс (bearing) от точки 1 к точке 2, в градусах.

    Результат: 0..360, где 0 — север, 90 — восток.
    """
    lat1 = radians(lat1_deg)
    lon1 = radians(lon1_deg)
    lat2 = radians(lat2_deg)
    lon2 = radians(lon2_deg)

    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)

    bearing = degrees(atan2(x, y))
    bearing = (bearing + 360.0) % 360.0
    return bearing


def destination_point(
    lat_deg: float,
    lon_deg: float,
    bearing_deg: float,
    distance_km: float,
) -> Tuple[float, float]:
    """
    Точка назначения при известном стартовом положении, курсе и дистанции.

    Возвращает (lat_deg, lon_deg).
    """
    lat = radians(lat_deg)
    lon = radians(lon_deg)
    bearing = radians(bearing_deg)

    ang_dist = distance_km / EARTH_RADIUS_KM

    lat2 = asin(
        sin(lat) * cos(ang_dist) + cos(lat) * sin(ang_dist) * cos(bearing)
    )
    lon2 = lon + atan2(
        sin(bearing) * sin(ang_dist) * cos(lat),
        cos(ang_dist) - sin(lat) * sin(lat2),
    )

    lat2_deg = degrees(lat2)
    lon2_deg = (degrees(lon2) + 540.0) % 360.0 - 180.0

    return lat2_deg, lon2_deg


def eta_hours(distance_km: float, ground_speed_kmh: float) -> float:
    """
    Оценка времени в пути (ETA) в часах.
    """
    if distance_km < 0 or ground_speed_kmh <= 0:
        raise ValueError("distance_km >= 0 и ground_speed_kmh > 0")
    return distance_km / ground_speed_kmh


def wind_corrected_heading(
    course_deg: float,
    tas_kts: float,
    wind_dir_from_deg: float,
    wind_speed_kts: float,
) -> Tuple[float, float]:
    """
    Расчёт поправки на ветер (WCA) и путевой скорости (ground speed).

    Возвращает:
      (heading_deg, ground_speed_kts)

    Где:
      - course_deg        — желаемый курс по земле (0..360)
      - tas_kts           — true airspeed (истинная скорость) в узлах
      - wind_dir_from_deg — направление, ОТКУДА дует ветер (метео-формат, 0..360)
      - wind_speed_kts    — скорость ветра в узлах (>= 0)

    Формулы классические:
      WCA = asin( (Vw / V) * sin(beta) )
      где beta = wind_dir_from - course

      GS = V * cos(WCA) - Vw * cos(beta)
    """
    from math import radians, degrees, asin, cos, sin

    if tas_kts <= 0:
        raise ValueError("tas_kts должен быть > 0")
    if wind_speed_kts < 0:
        raise ValueError("wind_speed_kts должен быть >= 0")

    course_rad = radians(course_deg)
    wind_from_rad = radians(wind_dir_from_deg)

    beta = wind_from_rad - course_rad

    ratio = wind_speed_kts / tas_kts
    x = ratio * sin(beta)

    if x > 1.0:
        x = 1.0
    elif x < -1.0:
        x = -1.0

    wca_rad = asin(x)
    heading_rad = course_rad + wca_rad

    gs = tas_kts * cos(wca_rad) - wind_speed_kts * cos(beta)

    heading_deg = (degrees(heading_rad) + 360.0) % 360.0
    return heading_deg, gs