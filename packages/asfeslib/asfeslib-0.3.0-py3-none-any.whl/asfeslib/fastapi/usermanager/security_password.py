from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Хэширование пароля для хранения в БД.
    """
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Проверка пароля. Возвращает True/False, а не кидает 500 при битом/левом хеше.
    """
    try:
        return pwd_context.verify(plain, hashed)
    except ValueError:
        return False
