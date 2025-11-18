# 🧠 ASFESLIB — универсальная библиотека для хакатонов и серверов ASFES
[![PyPI version](https://img.shields.io/pypi/v/asfeslib.svg)](https://pypi.org/project/asfeslib/)
![Python versions](https://img.shields.io/pypi/pyversions/asfeslib)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#)
[![ASFES](https://img.shields.io/badge/ASFES-Infrastructure-blue)](https://asfes.ru)

**ASFESLIB** — лёгкая асинхронная Python-библиотека для инфраструктуры ASFES (`asfes.ru`).  
Она объединяет всё, что нужно для быстрых серверов, API, интеграций, микросервисов, обработки данных, автоматизации и хакатонов.

---

## ⚠️ Важно: асинхронный Market API и обновлённые модули

Последние изменения:

- `asfeslib.utils.market_api` теперь **полностью асинхронный**:
  - `safe_get`, `CryptoAPI`, `StocksAPI`, `ForexAPI`, `Market.*` — вызываются только через `await`.
- `asfeslib.net.http.HTTPClient`:
  - строгая проверка схем (`http://` / `https://`),
  - относительные URL без `base_url` → `ValueError`,
  - логи **без query/fragment** (не светим токены).
- `asfeslib.core.logger.Logger`:
  - новый аргумент `level`,
  - нет дублирования хендлеров,
  - поддержка `colorlog`, аккуратный лог в файл.
- `asfeslib.net.mail.MailConfig`:
  - валидатор `retry_count` (1..10),
  - `rate_limit` — простая защита от спама.
- `asfeslib.core.sort.async_sort`:
  - валидирует `delay >= 0`, `delay < 0` → `ValueError`.
- Новый пакет **`asfeslib.aviation`**:
  - аэродинамика, навигация, OpenSky-клиент, мини-база аэропортов.

---

## 🚀 Основные возможности

| Модуль                           | Описание |
|---------------------------------|----------|
| `asfeslib.core.logger`          | Цветной логгер + вывод в файл, без дублирования хендлеров |
| `asfeslib.core.utils`           | Токены, timestamp, SHA-256, случайные строки, красивый JSON |
| `asfeslib.core.sort`            | Набор сортировок + учебный `async_sort` |
| `asfeslib.utils.conversions`    | 100+ универсальных конвертаций (Length, Mass, Time, Radio, Finance, Mechanics…) |
| `asfeslib.utils.market_api`     | **Async** Binance / Yahoo Finance / ER-API (кэш, ретраи, логирование) |
| `asfeslib.net.http`             | Асинхронный HTTP-клиент с логами, retry и безопасным URL-логированием |
| `asfeslib.net.mail`             | Асинхронная отправка писем через `smtplib` в `asyncio` + retry + rate limit |
| `asfeslib.databases`            | Асинхронные коннекторы MongoDB, PostgreSQL, MariaDB (без логирования паролей) |
| `asfeslib.weather`              | Полный клиент WeatherAPI (current/forecast/history/… ) |
| `asfeslib.aviation`             | Авиационные расчёты, навигация, OpenSky-клиент, мини-база аэропортов |

---

## 📦 Установка

### 🔧 Режим разработчика

```bash
git clone https://github.com/alxprgs/asfeslib.git
cd asfeslib
pip install -e .
```

### 🏭 Продакшн

```bash
pip install asfeslib
```

---

# 🟦 1. `asfeslib.core`

## 🪵 Логгер — `asfeslib.core.logger`

Упрощённая обёртка над `logging`, безопасная к многократному созданию.

```python
from asfeslib.core.logger import Logger

log = Logger(
    name="demo",
    log_to_file=True,
    log_file="logs/demo.log",
    level=20,  # logging.INFO
)

log.info("ASFESLIB запущен!")
log.warning("Предупреждение")
log.error("Ошибка")
log.debug("Отладочная информация")
```

Особенности:

- Не дублирует `StreamHandler`/`FileHandler` при повторном создании с тем же `name`.
- Если установлен `colorlog` — лог в консоль будет цветным.
- Параметр `log_to_file=True` создаёт лог-файл с UTF-8 и простым форматированием.

Уровни можно задавать как числа `logging.DEBUG` / `INFO` / `WARNING` и т.д.

---

## 🧰 Утилиты — `asfeslib.core.utils`

```python
from asfeslib.core import utils

utils.now_str()             # "2025-11-15 13:37:00" (локальное время)
utils.gen_token(32)         # безопасный hex-токен длиной 32 символа
utils.hash_text("Привет")   # SHA-256 от строки (utf-8)
utils.random_string(8)      # случайная a-zA-Z0-9 строка
utils.pretty_json({"a": 1, "msg": "Привет"})
```

Особенности:

- `gen_token(length: int)`:
  - гарантирует длину токена **не меньше** `length`,
  - поддерживает нечётные длины (`gen_token(31)` → строка длиной 31),
  - `length <= 0` → `ValueError`.
- `hash_text` **не** для паролей — только для хешей ID/логов. Для паролей нужны `bcrypt/scrypt/argon2`.

---

## 🔁 Сортировки — `asfeslib.core.sort`

```python
from asfeslib.core import sort
import asyncio

data = [5, 3, 4, 1, 2]

print(sort.quick_sort(data))
print(sort.merge_sort(data))
print(sort.sort_builtin(data, reverse=True))

# Учебная асинхронная пузырьковая сортировка
sorted_data = asyncio.run(sort.async_sort(data, delay=0.0))
```

Особенности:

- Есть несколько реализаций сортировок: `bubble_sort`, `insertion_sort`, `selection_sort`, `merge_sort`, `quick_sort`, `heap_sort`, `sort_builtin`.
- Все поддерживают `key=` и `reverse=`.
- `async_sort(data, key=…, delay=0.0)`:
  - имитация сортировки с визуализацией (например, через светодиоды),
  - `delay < 0` → `ValueError`,
  - `delay == 0` — без реальных задержек.

---

# 🟩 2. Конвертации — `asfeslib.utils.conversions`

Модуль содержит **100+ функций** в 17 категориях:

- `Length` — длина  
- `Mass` — масса  
- `Time` — время  
- `Temperature` — температура  
- `Area` — площадь  
- `Volume` — объём  
- `Speed` — скорость  
- `Energy` — энергия  
- `Pressure` — давление  
- `Data` — данные  
- `Angle` — углы  
- `Electricity` — электричество и закон Ома  
- `Math` — проценты, средние  
- `Mechanics` — сила, мощность, л.с., узлы  
- `Finance` — НДС, маржа, кредиты  
- `Radio` — dBm, частоты, длина волны  
- `Geophysics` — давление воды, g-force и т.п.

### Пример

```python
from asfeslib.utils.conversions import Length, Radio, Finance

Length.meters_to_km(2500)         # 2.5
Radio.dbm_to_mw(10)               # 10.0
Finance.loan_monthly_payment(
    principal=1_000_000,
    annual_rate_percent=12.0,
    years=20,
)
```

### Авто-инспекция API

```python
from asfeslib.utils.conversions import list_categories, list_functions

print(list_categories())          # ['length', 'mass', 'time', ...]
print(list_functions("length"))   # ['meters_to_km', 'km_to_meters', ...]
```

---

# 🟧 3. Market API (async) — `asfeslib.utils.market_api`

Единый асинхронный API для:

- **криптовалют** (Binance),
- **акций/ETF** (Yahoo Finance),
- **валют** (ER-API).

> ⚠️ Всё `awaitable`: `safe_get`, `CryptoAPI`, `StocksAPI`, `ForexAPI`, `Market.*`.

### Быстрый пример

```python
import asyncio
from asfeslib.utils.market_api import Market

async def main():
    btc = await Market.crypto_price("BTCUSDT")
    aapl = await Market.stock_price("AAPL")
    eur_usd = await Market.forex_rate("EUR", "USD")

    print("BTCUSDT:", btc)
    print("AAPL:", aapl)
    print("EUR/USD:", eur_usd)

asyncio.run(main())
```

### OHLC

```python
import asyncio
from asfeslib.utils.market_api import Market

async def main():
    candles = await Market.crypto_ohlc("BTCUSDT", interval="1h", limit=50)
    first = candles[0]
    print(first["open_time"], first["open"], first["close"])

asyncio.run(main())
```

Особенности:

- Внутренний кэш (TTL, отключается `use_cache=False` или `cache_ttl <= 0`).
- Ретраи с задержкой.
- Безопасный лог: URL в ошибках обрезается до `scheme://host/path` (без query/fragment), чтобы не светить токены.
- Явные исключения:
  - `APIError` — общие ошибки API/сети/формата,
  - `NotFoundError` — тикер/валюта не найдены.

---

# 🟦 4. HTTP-клиент — `asfeslib.net.http`

Асинхронный HTTP-клиент на базе `aiohttp`.

```python
import asyncio
from asfeslib.net.http import HTTPClient

async def main():
    async with HTTPClient("https://api.github.com") as http:
        repo = await http.get("/repos/alxprgs/asfeslib")
        print(repo["full_name"])

asyncio.run(main())
```

Особенности:

- Поддерживаются только схемы `http://` и `https://`.
- Относительный URL **без** `base_url` → `ValueError`.
- Любая другая схема (`file://`, `ftp://` и т.п.) → `ValueError`.
- Авто-разбор ответа:
  - `application/json` → `dict/list`,
  - `text/*` → `str`,
  - остальное → `bytes`.
- Ретраи с backoff.
- Логирование через `logging.getLogger(__name__)`:
  - в логах URL всегда без query/fragment (`?token=...` и `#frag` не выводятся).

Если нужно цветное логирование, можно сконфигурировать `logging` через `Logger` из `asfeslib.core.logger`.

---

# 🟨 5. SMTP-почта — `asfeslib.net.mail`

Асинхронная обёртка над стандартным `smtplib`, запускаемым через `asyncio.to_thread`.

Особенности:

- SSL / TLS,
- несколько попыток (`retry_count`, `retry_delay`),
- простая защита от спама — `rate_limit` (минимальный интервал между отправками),
- вложения,
- удобные Pydantic-модели: `MailConfig`, `MailMessage`, `MailAttachment`.

### Пример

```python
import asyncio
from asfeslib.net.mail import MailConfig, MailMessage, MailClient

cfg = MailConfig(
    host="mail.asfes.ru",
    port=465,
    username="hackathon@asfes.ru",
    password="***",
    from_name="ASFES Mailer",
    retry_count=3,
    retry_delay=1.0,
    rate_limit=0.0,
)

msg = MailMessage(
    to=["admin@asfes.ru"],
    subject="ASFESLIB test",
    body="Если ты читаешь это письмо — SMTP работает!",
    html=False,
)

async def main():
    async with MailClient(cfg) as mail:
        ok = await mail.send(msg, log=True)
        print("Sent:", ok)

asyncio.run(main())
```

> ⚠️ `retry_count` валидируется Pydantic: 1..10, иначе `ValueError`.

---

# 🗃 6. Базы данных — `asfeslib.databases`

Поддерживаются:

- MongoDB (`motor`),
- PostgreSQL (`psycopg[async]`),
- MariaDB/MySQL (`aiomysql`).

Основные функции:

- `asfeslib.databases.MongoDB.connect_mongo`
- `asfeslib.databases.PostgreSQL.connect_postgres`
- `asfeslib.databases.MySQL.connect_mariadb`
- агрегатор `asfeslib.databases.connect_database`

### Пример MongoDB

```python
import asyncio
from asfeslib.databases.MongoDB import MongoConnectScheme, connect_mongo

cfg = MongoConnectScheme(
    host="mongodb.asfes.ru",
    port=27017,
    username="user",
    password="password",
    db_name="hackathon_db",
)

async def main():
    client, db, ok = await connect_mongo(cfg)
    print("Mongo status:", ok)

asyncio.run(main())
```

Особенности:

- URL-ы собираются с учётом спецсимволов (`quote_plus` для логина/пароля).
- Для логирования используются «безопасные» описания (`host:port/db`), пароль в логах **никогда** не светится.
- Есть `serverSelectionTimeoutMS` / `connect_timeout`, чтобы не висеть вечно.

### Агрегатор — `connect_database`

```python
from asfeslib.databases import connect_database
from asfeslib.databases.MongoDB import MongoConnectScheme

cfg = MongoConnectScheme(db_name="hackathon_db")

client, db_or_conn, ok = await connect_database("mongo", cfg)
```

---

# 🌦 7. WeatherAPI — `asfeslib.weather`

Полный клиент WeatherAPI:

- `current` — текущая погода,
- `forecast` — прогноз,
- `history` — исторические данные,
- `future`,
- `astronomy`,
- `alerts`,
- `marine`,
- `bulk`,
- `ip`/`timezone` и т.д.

### Пример

```python
import asyncio
from asfeslib.weather import WeatherApiClient

async def main():
    async with WeatherApiClient(api_key="YOUR_WEATHERAPI_KEY") as w:
        resp = await w.current("Moscow")
        print(resp.location.name, resp.current.temp_c)

asyncio.run(main())
```

Особенности:

- Ленивый `httpx.AsyncClient` — создаётся только при первом запросе.
- Внутренние `_get` / `_post` с аккуратной типизацией.
- Все конечные методы возвращают Pydantic-модели (`CurrentResponse`, `ForecastResponse`, `AlertsResponse` и т.п.).

---

# ✈️ 8. Aviation — `asfeslib.aviation`

Набор утилит для авиационных задач:

- `aero` — атмосфера ISA, число Маха, подъёмная сила, скорость сваливания, fuel planning.
- `nav` — Haversine-расстояние, курсы, точка назначения, ETA, ветровые поправки.
- `api` — асинхронный клиент OpenSky Network (live-трафик самолётов).
- `data` — мини-база аэропортов (несколько популярных в мире).

### Базовые расчёты

```python
from asfeslib.aviation import (
    air_density_isa,
    speed_of_sound,
    mach_to_kmh,
    kmh_to_mach,
    stall_speed,
)

rho0 = air_density_isa(0)             # ≈ 1.225 кг/м³
a0 = speed_of_sound(0)                # ≈ 340 м/с
m = kmh_to_mach(900, altitude_m=11000)
vs = stall_speed(
    weight_kg=70000,
    wing_area_m2=122,
    cl_max=2.0,
    altitude_m=0,
)
```

### Навигация

```python
from asfeslib.aviation import (
    haversine_distance_km,
    initial_bearing_deg,
    destination_point,
    eta_hours,
    wind_corrected_heading,
)

d = haversine_distance_km(55.75, 37.61, 59.93, 30.33)   # Москва – СПб
bearing = initial_bearing_deg(55.75, 37.61, 59.93, 30.33)

lat2, lon2 = destination_point(55.0, 37.0, bearing_deg=45, distance_km=100)
eta = eta_hours(distance_km=d, ground_speed_kmh=800)

heading, gs = wind_corrected_heading(
    course_deg=90,
    tas_kts=120,
    wind_dir_from_deg=0,
    wind_speed_kts=20,
)
```

### Аэропорты

```python
from asfeslib.aviation import get_airport, airport_coords, runway_length_m

ap = get_airport("UUDD")      # ICAO или IATA (DME)
coords = airport_coords("DME")
rw_len = runway_length_m("UUEE")
```

### OpenSky клиент

```python
import asyncio
from asfeslib.aviation import OpenSkyClient

async def main():
    async with OpenSkyClient() as sky:
        data = await sky.live_area(
            min_lat=54.0, min_lon=35.0,
            max_lat=57.0, max_lon=39.0,  # район Москвы
        )
        print("Бортов в зоне:", len(data))

asyncio.run(main())
```

> ⚠️ OpenSky API публичный, без ключа, но с лимитами.  
> При превышении лимита может прилететь 429 — в live-тестах это корректно обрабатывается как `skip`.

---

# 🧪 Тесты и live-режим

Все основные модули покрыты тестами `pytest`.

### Обычные тесты

```bash
pytest
```

### Live-тесты

Live-тесты **по умолчанию отключены**, включаются маркером `live`:

```bash
pytest -m live
```

Используются:

- `tests/test_mail_live.py`
- `tests/test_market_live.py`
- `tests/test_weather_live_api.py`
- `tests/test_aviation_live.py`

Часть из них требует переменных окружения:

```powershell
# PowerShell пример
$env:ASFESLIB_SMTP_USER = "hackathon@asfes.ru"
$env:ASFESLIB_SMTP_PASSWORD = "SMTP_PASSWORD"
$env:ASFESLIB_WEATHER_API_KEY = "YOUR_WEATHERAPI_KEY"
```

Часть тестов может быть **скипнута**:

- Yahoo Finance / OpenSky → при `HTTP 429` (rate limit).
- WeatherAPI → если нет `ASFESLIB_WEATHER_API_KEY`.

---

# 📂 Структура проекта

```text
asfeslib/
│
├── core/
│   ├── logger.py
│   ├── utils.py
│   └── sort.py
│
├── utils/
│   ├── conversions.py
│   └── market_api.py
│
├── databases/
│   ├── MongoDB.py
│   ├── MySQL.py
│   ├── PostgreSQL.py
│   └── __init__.py
│
├── net/
│   ├── http.py
│   └── mail.py
│
├── weather/
│   ├── client.py
│   ├── models/
│   └── ...
│
├── aviation/
│   ├── __init__.py
│   ├── aero.py
│   ├── nav.py
│   ├── api.py
│   └── data.py
│
└── tests/
```

---

# 🛠 Использование в FastAPI

Пример подключения БД и логгера в FastAPI-приложении:

```python
from fastapi import FastAPI
from asfeslib.core.logger import Logger
from asfeslib.databases import connect_database
from asfeslib.databases.MongoDB import MongoConnectScheme

log = Logger("api")
app = FastAPI()

@app.on_event("startup")
async def startup():
    cfg = MongoConnectScheme(db_name="hackathon_db")
    client, app.state.db, ok = await connect_database("mongo", cfg)
    if ok:
        log.info("MongoDB подключена!")
    else:
        log.error("Не удалось подключиться к MongoDB")
```

---

# 📜 Лицензия

MIT License

---

# 👤 Контакты

- 🌐 https://asfes.ru/
- 🔧 GitHub: https://github.com/alxprgs/
- ✉️ Автор: Александр

---