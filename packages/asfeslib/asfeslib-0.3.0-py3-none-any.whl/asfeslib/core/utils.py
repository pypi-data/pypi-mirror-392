import json
import hashlib
import secrets
import string
from datetime import datetime


def now_str() -> str:
    """Возвращает текущий timestamp в строковом формате (локальное время)."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def gen_token(length: int = 32) -> str:
    """
    Генерация безопасного hex-токена длиной не менее `length` символов.

    Для типичных значений (32, 64 и т.п.) длина будет совпадать ровно.
    """
    if length <= 0:
        raise ValueError("length должен быть > 0")
    nbytes = (length + 1) // 2
    return secrets.token_hex(nbytes)[:length]


def hash_text(text: str) -> str:
    """
    Хэширование строки SHA256.

    Важно: не использовать для хранения паролей.
    Для паролей нужны специализированные алгоритмы (bcrypt/scrypt/argon2).
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def random_string(length: int = 8) -> str:
    """Случайная строка (для тестовых логинов, кодов и т.п.)."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def pretty_json(data) -> str:
    """Красивый JSON-вывод (удобно для логов и отладки)."""
    return json.dumps(data, indent=4, ensure_ascii=False)
