"""
ASFESLIB Aviation — набор утилит для авиации.

Содержит:
- aero  — аэродинамика, ISA, Mach, сваливание, топливо
- nav   — навигация, геодезия, курс, ETA, ветер
- api   — клиент OpenSky Network (live-трафик самолётов)
- data  — мини-база аэропортов и утилиты
"""

from . import aero, nav, api, data
from .aero import (
    air_density_isa,
    speed_of_sound,
    mach_to_kmh,
    kmh_to_mach,
    lift,
    stall_speed,
    density_altitude,
    fuel_needed,
)
from .nav import (
    haversine_distance_km,
    initial_bearing_deg,
    destination_point,
    eta_hours,
    wind_corrected_heading,
)
from .api import OpenSkyClient
from .data import (
    AIRPORTS,
    get_airport,
    airport_coords,
    runway_length_m,
)

__all__ = [
    "aero",
    "nav",
    "api",
    "data",
    "air_density_isa",
    "speed_of_sound",
    "mach_to_kmh",
    "kmh_to_mach",
    "lift",
    "stall_speed",
    "density_altitude",
    "fuel_needed",
    "haversine_distance_km",
    "initial_bearing_deg",
    "destination_point",
    "eta_hours",
    "wind_corrected_heading",
    "OpenSkyClient",
    "AIRPORTS",
    "get_airport",
    "airport_coords",
    "runway_length_m",
]
