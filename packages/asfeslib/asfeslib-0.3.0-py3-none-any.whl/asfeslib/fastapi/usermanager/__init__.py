from __future__ import annotations

from fastapi import APIRouter
from asfeslib.core.logger import Logger

from .manager import UserManager, RootUserConfig

router = APIRouter()
logger = Logger(__name__)

bd_type: str | None = None
bd = None

JWT_SECRET_KEY: str | None = None
JWT_ALGORITHM: str = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MIN: int = 60


def init_user_manager(
    db_type: str,
    db,
    jwt_secret_key: str,
    jwt_algorithm: str = "HS256",
    access_token_expires_min: int = 60,
) -> UserManager:
    """
    DEPRECATED: используй UserManager(...) напрямую.

    Оставлено для обратной совместимости:
    - заполняет глобальные переменные (bd_type, bd, JWT_*),
    - создаёт и возвращает экземпляр UserManager.

    Вызывается 1 раз при старте FastAPI-приложения.
    """
    global bd_type, bd, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MIN

    bd_type = db_type
    bd = db

    JWT_SECRET_KEY = jwt_secret_key
    JWT_ALGORITHM = jwt_algorithm
    JWT_ACCESS_TOKEN_EXPIRE_MIN = access_token_expires_min

    logger.warning(
        "init_user_manager() устарел. "
        "Используй asfeslib.fastapi.usermanager.UserManager напрямую."
    )

    manager = UserManager(
        db_type=db_type,
        db=db,
        jwt_secret_key=jwt_secret_key,
        jwt_algorithm=jwt_algorithm,
        access_token_ttl=access_token_expires_min,
    )

    logger.info(
        f"UserManager initialized: db_type={db_type}, "
        f"alg={jwt_algorithm}, ttl={access_token_expires_min}m"
    )

    return manager


__all__ = [
    "router",
    "logger",
    "UserManager",
    "RootUserConfig",
    "init_user_manager",
]
