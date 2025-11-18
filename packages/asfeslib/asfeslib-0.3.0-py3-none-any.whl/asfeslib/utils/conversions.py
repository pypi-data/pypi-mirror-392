"""
ASFESLIB — Универсальные конвертации единиц измерения.
100+ функций, сгруппированных по категориям.

Категории:
- Length       — длина
- Mass         — масса
- Time         — время
- Temperature  — температура
- Area         — площадь
- Volume       — объём
- Speed        — скорость
- Energy       — энергия
- Pressure     — давление
- Data         — цифровые данные
- Angle        — углы
- Electricity  — электрические величины
- Math         — математика / проценты
- Mechanics    — механика / мощность / сила
- Finance      — финансы
- Radio        — радиотехника и частоты
- Geophysics   — геофизика / плотность / освещённость

Также есть утилиты для авто-TOC:
- list_categories()
- list_functions(category: str | None = None)
- get_converter(category: str)
- get_function(category: str, name: str)
"""

from __future__ import annotations

from math import pi, log10, sqrt
from typing import Callable, Dict, List, Type

class Length:
    """Конвертации единиц длины"""

    @staticmethod
    def meters_to_km(m: float) -> float:
        """Преобразование метров в километры"""
        return m / 1000

    @staticmethod
    def km_to_m(km: float) -> float:
        """Преобразование километров в метры"""
        return km * 1000

    @staticmethod
    def meters_to_cm(m: float) -> float:
        """Преобразование метров в сантиметры"""
        return m * 100

    @staticmethod
    def cm_to_m(cm: float) -> float:
        """Преобразование сантиметров в метры"""
        return cm / 100

    @staticmethod
    def inches_to_cm(inch: float) -> float:
        """Преобразование дюймов в сантиметры"""
        return inch * 2.54

    @staticmethod
    def cm_to_inches(cm: float) -> float:
        """Преобразование сантиметров в дюймы"""
        return cm / 2.54

    @staticmethod
    def feet_to_m(ft: float) -> float:
        """Преобразование футов в метры"""
        return ft * 0.3048

    @staticmethod
    def m_to_feet(m: float) -> float:
        """Преобразование метров в футы"""
        return m / 0.3048

    @staticmethod
    def miles_to_km(mi: float) -> float:
        """Преобразование миль в километры"""
        return mi * 1.60934

    @staticmethod
    def km_to_miles(km: float) -> float:
        """Преобразование километров в мили"""
        return km / 1.60934

class Mass:
    """Конвертации массы"""

    @staticmethod
    def kg_to_g(kg: float) -> float:
        """Преобразование килограммов в граммы"""
        return kg * 1000

    @staticmethod
    def g_to_kg(g: float) -> float:
        """Преобразование граммов в килограммы"""
        return g / 1000

    @staticmethod
    def kg_to_lb(kg: float) -> float:
        """Преобразование килограммов в фунты"""
        return kg * 2.20462

    @staticmethod
    def lb_to_kg(lb: float) -> float:
        """Преобразование фунтов в килограммы"""
        return lb / 2.20462

    @staticmethod
    def kg_to_tons(kg: float) -> float:
        """Преобразование килограммов в тонны"""
        return kg / 1000

    @staticmethod
    def tons_to_kg(t: float) -> float:
        """Преобразование тонн в килограммы"""
        return t * 1000


class Time:
    """Конвертации времени"""

    @staticmethod
    def sec_to_min(s: float) -> float:
        """Преобразование секунд в минуты"""
        return s / 60

    @staticmethod
    def min_to_sec(m: float) -> float:
        """Преобразование минут в секунды"""
        return m * 60

    @staticmethod
    def min_to_hours(m: float) -> float:
        """Преобразование минут в часы"""
        return m / 60

    @staticmethod
    def hours_to_min(h: float) -> float:
        """Преобразование часов в минуты"""
        return h * 60

    @staticmethod
    def hours_to_days(h: float) -> float:
        """Преобразование часов в дни"""
        return h / 24

    @staticmethod
    def days_to_hours(d: float) -> float:
        """Преобразование дней в часы"""
        return d * 24


class Temperature:
    """Конвертации температуры"""

    @staticmethod
    def c_to_f(c: float) -> float:
        """Перевод градусов Цельсия в Фаренгейты"""
        return c * 9 / 5 + 32

    @staticmethod
    def f_to_c(f: float) -> float:
        """Перевод градусов Фаренгейта в Цельсий"""
        return (f - 32) * 5 / 9

    @staticmethod
    def c_to_k(c: float) -> float:
        """Перевод градусов Цельсия в Кельвины"""
        return c + 273.15

    @staticmethod
    def k_to_c(k: float) -> float:
        """Перевод Кельвинов в градусы Цельсия"""
        return k - 273.15

class Area:
    """Конвертации площади"""

    @staticmethod
    def m2_to_km2(m2: float) -> float:
        """Квадратные метры в квадратные километры"""
        return m2 / 1_000_000

    @staticmethod
    def km2_to_m2(km2: float) -> float:
        """Квадратные километры в квадратные метры"""
        return km2 * 1_000_000

    @staticmethod
    def m2_to_cm2(m2: float) -> float:
        """Квадратные метры в квадратные сантиметры"""
        return m2 * 10_000

    @staticmethod
    def cm2_to_m2(cm2: float) -> float:
        """Квадратные сантиметры в квадратные метры"""
        return cm2 / 10_000

    @staticmethod
    def acres_to_m2(ac: float) -> float:
        """Акры в квадратные метры"""
        return ac * 4046.856

    @staticmethod
    def m2_to_acres(m2: float) -> float:
        """Квадратные метры в акры"""
        return m2 / 4046.856

class Volume:
    """Конвертации объёма"""

    @staticmethod
    def liters_to_ml(l: float) -> float:
        """Литры в миллилитры"""
        return l * 1000

    @staticmethod
    def ml_to_liters(ml: float) -> float:
        """Миллилитры в литры"""
        return ml / 1000

    @staticmethod
    def liters_to_gallons(l: float) -> float:
        """Литры в галлоны"""
        return l / 3.78541

    @staticmethod
    def gallons_to_liters(g: float) -> float:
        """Галлоны в литры"""
        return g * 3.78541

    @staticmethod
    def m3_to_liters(m3: float) -> float:
        """Кубические метры в литры"""
        return m3 * 1000

    @staticmethod
    def liters_to_m3(l: float) -> float:
        """Литры в кубические метры"""
        return l / 1000


class Speed:
    """Конвертации скорости"""

    @staticmethod
    def mps_to_kmph(mps: float) -> float:
        """Метры/с в километры/ч"""
        return mps * 3.6

    @staticmethod
    def kmph_to_mps(kmph: float) -> float:
        """Километры/ч в метры/с"""
        return kmph / 3.6

    @staticmethod
    def mph_to_kmph(mph: float) -> float:
        """Мили/ч в километры/ч"""
        return mph * 1.60934

    @staticmethod
    def kmph_to_mph(kmph: float) -> float:
        """Километры/ч в мили/ч"""
        return kmph / 1.60934

class Energy:
    """Конвертации энергии"""

    @staticmethod
    def joules_to_cal(j: float) -> float:
        """Джоули в калории"""
        return j / 4.184

    @staticmethod
    def cal_to_joules(cal: float) -> float:
        """Калории в джоули"""
        return cal * 4.184

    @staticmethod
    def kwh_to_joules(kwh: float) -> float:
        """Киловатт-часы в джоули"""
        return kwh * 3_600_000

    @staticmethod
    def joules_to_kwh(j: float) -> float:
        """Джоули в киловатт-часы"""
        return j / 3_600_000

class Pressure:
    """Конвертации давления"""

    @staticmethod
    def atm_to_pa(a: float) -> float:
        """Атмосферы в паскали"""
        return a * 101_325

    @staticmethod
    def pa_to_atm(pa: float) -> float:
        """Паскали в атмосферы"""
        return pa / 101_325

    @staticmethod
    def bar_to_pa(b: float) -> float:
        """Бары в паскали"""
        return b * 100_000

    @staticmethod
    def pa_to_bar(pa: float) -> float:
        """Паскали в бары"""
        return pa / 100_000

class Data:
    """Конвертации цифровых данных"""

    @staticmethod
    def bytes_to_kb(b: float) -> float:
        """Байты в килобайты (1024)"""
        return b / 1024

    @staticmethod
    def kb_to_bytes(kb: float) -> float:
        """Килобайты в байты"""
        return kb * 1024

    @staticmethod
    def kb_to_mb(kb: float) -> float:
        """Килобайты в мегабайты"""
        return kb / 1024

    @staticmethod
    def mb_to_kb(mb: float) -> float:
        """Мегабайты в килобайты"""
        return mb * 1024

    @staticmethod
    def mb_to_gb(mb: float) -> float:
        """Мегабайты в гигабайты"""
        return mb / 1024

    @staticmethod
    def gb_to_mb(gb: float) -> float:
        """Гигабайты в мегабайты"""
        return gb * 1024

class Angle:
    """Конвертации углов"""

    @staticmethod
    def deg_to_rad(deg: float) -> float:
        """Градусы в радианы"""
        return deg * pi / 180

    @staticmethod
    def rad_to_deg(rad: float) -> float:
        """Радианы в градусы"""
        return rad * 180 / pi


class Electricity:
    """Электрические конвертации + закон Ома"""

    @staticmethod
    def volts_to_millivolts(v: float) -> float:
        """Вольты в милливольты"""
        return v * 1000

    @staticmethod
    def millivolts_to_volts(mv: float) -> float:
        """Милливольты в вольты"""
        return mv / 1000

    @staticmethod
    def amps_to_milliamps(a: float) -> float:
        """Амперы в миллиамперы"""
        return a * 1000

    @staticmethod
    def milliamps_to_amps(ma: float) -> float:
        """Миллиамперы в амперы"""
        return ma / 1000

    @staticmethod
    def ohm_law_u(i: float, r: float) -> float:
        """Вычисление напряжения по закону Ома (U = I * R)"""
        return i * r

    @staticmethod
    def ohm_law_i(u: float, r: float) -> float:
        """Вычисление силы тока по закону Ома (I = U / R)"""
        return u / r

    @staticmethod
    def ohm_law_r(u: float, i: float) -> float:
        """Вычисление сопротивления по закону Ома (R = U / I)"""
        return u / i

class Math:
    """Базовые математические и процентные конвертации"""

    @staticmethod
    def percent_of(value: float, percent: float) -> float:
        """percent% от value"""
        return value * percent / 100

    @staticmethod
    def percent_change(old: float, new: float) -> float:
        """Процент изменения от old к new"""
        if old == 0:
            raise ValueError("old не должен быть 0 для percent_change")
        return (new - old) / old * 100

    @staticmethod
    def add_percent(value: float, percent: float) -> float:
        """Увеличение значения на процент"""
        return value * (1 + percent / 100)

    @staticmethod
    def subtract_percent(value: float, percent: float) -> float:
        """Уменьшение значения на процент"""
        return value * (1 - percent / 100)

    @staticmethod
    def ratio(a: float, b: float) -> float:
        """Отношение a к b"""
        return a / b

    @staticmethod
    def average(a: float, b: float) -> float:
        """Среднее арифметическое двух чисел"""
        return (a + b) / 2

    @staticmethod
    def harmonic_mean(a: float, b: float) -> float:
        """Среднее гармоническое"""
        return 2 * a * b / (a + b)

    @staticmethod
    def geometric_mean(a: float, b: float) -> float:
        """Среднее геометрическое"""
        return sqrt(a * b)

    @staticmethod
    def sq(x: float) -> float:
        """Квадрат числа"""
        return x * x

    @staticmethod
    def cube(x: float) -> float:
        """Куб числа"""
        return x * x * x


class Mechanics:
    """Физические конвертации и расчёты"""

    @staticmethod
    def newton_to_kgf(n: float) -> float:
        """Ньютоны в кгс"""
        return n / 9.80665

    @staticmethod
    def kgf_to_newton(kgf: float) -> float:
        """Кгс в ньютоны"""
        return kgf * 9.80665

    @staticmethod
    def joules_to_wh(j: float) -> float:
        """Джоули в ватт-часы"""
        return j / 3600

    @staticmethod
    def wh_to_joules(wh: float) -> float:
        """Ватт-часы в джоули"""
        return wh * 3600

    @staticmethod
    def watts_to_hp(w: float) -> float:
        """Ватты в лошадиные силы"""
        return w / 745.7

    @staticmethod
    def hp_to_watts(hp: float) -> float:
        """Лошадиные силы в ватты"""
        return hp * 745.7

    @staticmethod
    def mps_to_knots(mps: float) -> float:
        """М/с в узлы"""
        return mps * 1.94384

    @staticmethod
    def knots_to_mps(knots: float) -> float:
        """Узлы в м/с"""
        return knots / 1.94384

    @staticmethod
    def kg_to_newton(kg: float) -> float:
        """Масса (кг) в силу тяжести (Н)"""
        return kg * 9.80665

    @staticmethod
    def newton_to_kg(n: float) -> float:
        """Сила в ньютонах в массу (кг)"""
        return n / 9.80665


class Finance:
    """Финансовые расчёты"""

    @staticmethod
    def rub_to_kop(r: float) -> float:
        """Рубли в копейки"""
        return r * 100

    @staticmethod
    def kop_to_rub(k: float) -> float:
        """Копейки в рубли"""
        return k / 100

    @staticmethod
    def usd_to_cents(usd: float) -> float:
        """Доллары в центы"""
        return usd * 100

    @staticmethod
    def cents_to_usd(cents: float) -> float:
        """Центы в доллары"""
        return cents / 100

    @staticmethod
    def monthly_to_yearly(rate: float) -> float:
        """Перевод месячной ставки (%) в годовую эффективную (%)"""
        return (1 + rate / 100) ** 12 * 100 - 100

    @staticmethod
    def yearly_to_monthly(rate: float) -> float:
        """Годовая ставка (%) в эквивалентную месячную (%)"""
        return ((1 + rate / 100) ** (1 / 12) - 1) * 100

    @staticmethod
    def loan_monthly_payment(sum_: float, rate: float, years: int) -> float:
        """Аннуитетный платеж по кредиту"""
        n = years * 12
        if rate == 0:
            return sum_ / n
        r = rate / 1200
        return sum_ * r * (1 + r) ** n / ((1 + r) ** n - 1)

    @staticmethod
    def profit_from_margin(cost: float, margin: float) -> float:
        """Прибыль при наценке (%)"""
        return cost * margin / 100

    @staticmethod
    def final_price_with_margin(cost: float, margin: float) -> float:
        """Итоговая цена с наценкой (%)"""
        return cost * (1 + margin / 100)

    @staticmethod
    def vat_amount(price: float, vat: float = 20) -> float:
        """Сумма НДС в цене"""
        return price * vat / 100

class Radio:
    """Конвертации в радиотехнике"""

    @staticmethod
    def hz_to_khz(hz: float) -> float:
        """Герцы в килогерцы"""
        return hz / 1000

    @staticmethod
    def khz_to_hz(khz: float) -> float:
        """Килогерцы в герцы"""
        return khz * 1000

    @staticmethod
    def khz_to_mhz(khz: float) -> float:
        """Килогерцы в мегагерцы"""
        return khz / 1000

    @staticmethod
    def mhz_to_khz(mhz: float) -> float:
        """Мегагерцы в килогерцы"""
        return mhz * 1000

    @staticmethod
    def mhz_to_ghz(mhz: float) -> float:
        """Мегагерцы в гигагерцы"""
        return mhz / 1000

    @staticmethod
    def ghz_to_mhz(ghz: float) -> float:
        """Гигагерцы в мегагерцы"""
        return ghz * 1000

    @staticmethod
    def wavelength_from_freq(freq_hz: float) -> float:
        """Длина волны по частоте (λ = c / f)"""
        return 299_792_458 / freq_hz

    @staticmethod
    def freq_from_wavelength(wavelength_m: float) -> float:
        """Частота по длине волны (f = c / λ)"""
        return 299_792_458 / wavelength_m

    @staticmethod
    def dbm_to_mw(dbm: float) -> float:
        """Мощность в dBm → милливатты"""
        return 10 ** (dbm / 10)

    @staticmethod
    def mw_to_dbm(mw: float) -> float:
        """Милливатты → dBm"""
        if mw <= 0:
            raise ValueError("mw должно быть > 0 для перевода в dBm")
        return 10 * log10(mw)


class Geophysics:
    """Геофизика и плотность"""

    @staticmethod
    def density_mass(volume: float, density: float) -> float:
        """Масса = объём * плотность"""
        return volume * density

    @staticmethod
    def density_volume(mass: float, density: float) -> float:
        """Объём = масса / плотность"""
        return mass / density

    @staticmethod
    def water_pressure(depth_m: float) -> float:
        """Давление воды по глубине (приблизительно, Па)"""
        return depth_m * 9800

    @staticmethod
    def air_pressure(height_m: float) -> float:
        """Приближённое давление воздуха на высоте (барометрическая формула)"""
        return 101_325 * (1 - 2.25577e-5 * height_m) ** 5.25588

    @staticmethod
    def gforce_from_acc(acc: float) -> float:
        """Ускорение в g"""
        return acc / 9.80665

    @staticmethod
    def acc_from_gforce(g: float) -> float:
        """g в м/с^2"""
        return g * 9.80665

    @staticmethod
    def rad_per_s_to_rpm(rad: float) -> float:
        """Рад/с в об/мин"""
        return rad * 60 / (2 * pi)

    @staticmethod
    def rpm_to_rad_per_s(rpm: float) -> float:
        """Об/мин в рад/с"""
        return rpm * (2 * pi) / 60

    @staticmethod
    def lux_to_lm(m2: float, lux: float) -> float:
        """Люкс → люмены (люкс * площадь)"""
        return m2 * lux

    @staticmethod
    def lm_to_lux(lm: float, m2: float) -> float:
        """Люмены → люкс (люмены / площадь)"""
        return lm / m2

_CONVERSION_CATEGORIES: Dict[str, Type] = {
    "length": Length,
    "mass": Mass,
    "time": Time,
    "temperature": Temperature,
    "area": Area,
    "volume": Volume,
    "speed": Speed,
    "energy": Energy,
    "pressure": Pressure,
    "data": Data,
    "angle": Angle,
    "electricity": Electricity,
    "math": Math,
    "mechanics": Mechanics,
    "finance": Finance,
    "radio": Radio,
    "geophysics": Geophysics,
}


def list_categories() -> List[str]:
    """Список доступных категорий конвертаций"""
    return sorted(_CONVERSION_CATEGORIES.keys())


def _iter_public_static_methods(cls: Type) -> Dict[str, Callable]:
    """Получить публичные статические методы класса"""
    result: Dict[str, Callable] = {}
    for name in dir(cls):
        if name.startswith("_"):
            continue
        attr = getattr(cls, name)
        if callable(attr):
            result[name] = attr
    return result


def list_functions(category: str | None = None) -> Dict[str, Dict[str, str]]:
    """
    Вернуть структуру:
    {
        "category": {
            "function_name": "docstring или ''"
        }
    }

    Если category None — вернуть по всем категориям.
    """
    if category is not None:
        cat_key = category.lower()
        if cat_key not in _CONVERSION_CATEGORIES:
            raise KeyError(f"Неизвестная категория: {category}")
        cls = _CONVERSION_CATEGORIES[cat_key]
        funcs = _iter_public_static_methods(cls)
        return {
            cat_key: {
                name: (func.__doc__ or "").strip()
                for name, func in funcs.items()
            }
        }

    out: Dict[str, Dict[str, str]] = {}
    for cat_key, cls in _CONVERSION_CATEGORIES.items():
        funcs = _iter_public_static_methods(cls)
        out[cat_key] = {
            name: (func.__doc__ or "").strip()
            for name, func in funcs.items()
        }
    return out


def get_converter(category: str) -> Type:
    """Получить класс-конвертер по его категории"""
    cat_key = category.lower()
    if cat_key not in _CONVERSION_CATEGORIES:
        raise KeyError(f"Неизвестная категория: {category}")
    return _CONVERSION_CATEGORIES[cat_key]


def get_function(category: str, name: str) -> Callable:
    """Получить конкретную функцию конвертации по имени и категории"""
    cls = get_converter(category)
    methods = _iter_public_static_methods(cls)
    if name not in methods:
        raise KeyError(f"В категории '{category}' нет функции '{name}'")
    return methods[name]


__all__ = [
    "Length",
    "Mass",
    "Time",
    "Temperature",
    "Area",
    "Volume",
    "Speed",
    "Energy",
    "Pressure",
    "Data",
    "Angle",
    "Electricity",
    "Math",
    "Mechanics",
    "Finance",
    "Radio",
    "Geophysics",
    "list_categories",
    "list_functions",
    "get_converter",
    "get_function",
]
