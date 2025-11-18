"""
Аэродинамика и атмосфера (упрощённые модели для расчётов).

Цели:
- не претендует на точность проф. софта,
- но даёт адекватные оценки для учебных/хакатонных задач.
"""

from __future__ import annotations

from math import sqrt
from typing import Optional

T0 = 288.15         # K, температура на уровне моря
P0 = 101325.0       # Па, давление на уровне моря
L  = -0.0065        # K/м, градиент температуры
R  = 287.05         # Дж/(кг·K), газовая постоянная воздуха
G0 = 9.80665        # м/с², ускорение свободного падения


def air_density_isa(altitude_m: float) -> float:
    """
    Плотность воздуха по стандартной атмосфере ISA до ~11 км.
    Возвращает кг/м³.
    """
    if altitude_m < 0:
        altitude_m = 0

    T = T0 + L * altitude_m
    if T <= 0:
        T = 1.0

    P = P0 * (T / T0) ** (-G0 / (L * R))

    # Плотность
    rho = P / (R * T)
    return rho


def speed_of_sound(altitude_m: float = 0.0) -> float:
    """
    Скорость звука в м/с по ISA на заданной высоте.
    a = sqrt(gamma * R * T), gamma ≈ 1.4
    """
    gamma = 1.4
    if altitude_m < 0:
        altitude_m = 0
    T = T0 + L * altitude_m
    if T <= 0:
        T = 1.0
    return sqrt(gamma * R * T)


def mach_to_kmh(mach: float, altitude_m: float = 0.0) -> float:
    """
    Конвертация числа Маха в км/ч с учётом высоты.
    """
    a = speed_of_sound(altitude_m)  # м/с
    return mach * a * 3.6


def kmh_to_mach(speed_kmh: float, altitude_m: float = 0.0) -> float:
    """
    Конвертация скорости км/ч в число Маха на заданной высоте.
    """
    a = speed_of_sound(altitude_m)  # м/с
    return (speed_kmh / 3.6) / a


def lift(rho: float, velocity_mps: float, wing_area_m2: float, cl: float) -> float:
    """
    Подъёмная сила:
        L = 0.5 * rho * v^2 * S * CL

    Возвращает силу в Ньютонах.
    """
    return 0.5 * rho * velocity_mps**2 * wing_area_m2 * cl


def stall_speed(
    weight_kg: float,
    wing_area_m2: float,
    cl_max: float,
    rho: Optional[float] = None,
    altitude_m: Optional[float] = None,
) -> float:
    """
    Скорость сваливания по формуле:

        Vstall = sqrt( (2 * W) / (rho * S * CLmax) )

    где:
    - W     — вес (Н) = масса (кг) * g
    - rho   — плотность (кг/м³)
    - S     — площадь крыла (м²)
    - CLmax — максимальный коэффициент подъёмной силы

    Возвращает скорость в м/с.
    """
    if rho is None:
        alt = altitude_m or 0.0
        rho = air_density_isa(alt)

    if rho <= 0 or wing_area_m2 <= 0 or cl_max <= 0:
        raise ValueError("rho, wing_area_m2 и cl_max должны быть > 0")

    weight_n = weight_kg * G0
    v_stall = sqrt(2 * weight_n / (rho * wing_area_m2 * cl_max))
    return v_stall


def density_altitude(
    temp_c: float,
    pressure_hpa: float,
    elevation_m: float = 0.0,
) -> float:
    """
    Приближённый расчёт density altitude (высоты плотности), м.

    Используется простая оценка:
      DA ≈ elevation + (120 * (OAT - TISA))

    где:
      OAT  — фактическая температура на высоте (°C)
      TISA — стандартная ISA температура на этой высоте (°C)

    В расчёт также корректируемся по давлению относительно 1013 гПа.
    """
    t_isa_c = 15.0 + L * elevation_m

    oat = temp_c
    delta_t = oat - t_isa_c

    da_temp = elevation_m + 120.0 * delta_t

    delta_p = 1013.0 - pressure_hpa
    da_pres = delta_p * 9.0

    return da_temp + da_pres


def fuel_needed(
    distance_km: float,
    burn_kg_per_h: float,
    speed_kmh: float,
    reserve_factor: float = 1.3,
) -> float:
    """
    Оценка топлива для перелёта.

    distance_km     — дистанция в км
    burn_kg_per_h   — расход топлива (кг/ч)
    speed_kmh       — крейсерская скорость (км/ч)
    reserve_factor  — запас по топливу (по умолчанию 30%)

    Возвращает массу топлива в кг.
    """
    if distance_km < 0 or burn_kg_per_h <= 0 or speed_kmh <= 0:
        raise ValueError("distance_km >= 0, burn_kg_per_h > 0, speed_kmh > 0")

    flight_hours = distance_km / speed_kmh
    base_fuel = burn_kg_per_h * flight_hours
    return base_fuel * reserve_factor
