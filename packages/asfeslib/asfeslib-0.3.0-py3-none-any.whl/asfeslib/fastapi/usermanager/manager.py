from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from asfeslib.core.logger import Logger

from .router import get_user_router
from .security import JWTManager

logger = Logger(__name__)


class RootUserConfig(BaseModel):
    login: str
    email: EmailStr
    password: str


class UserManager:
    def __init__(
        self,
        db_type: str,
        db,
        jwt_secret_key: str,
        jwt_algorithm: str = "HS256",
        access_token_ttl: int = 15,
        refresh_token_ttl: int = 30 * 24 * 60,  # 30 дней
        allowed_roles: Optional[list[str]] = None,
        enable_basic_rate_limit: bool = False,
        max_login_attempts: int = 5,
        login_block_minutes: int = 5,
    ):
        self.db_type = db_type
        self.db = db

        self.jwt = JWTManager(
            secret_key=jwt_secret_key,
            algorithm=jwt_algorithm,
            access_token_ttl=access_token_ttl,
            refresh_token_ttl=refresh_token_ttl,
        )

        self.allowed_roles = allowed_roles or ["user", "admin", "dev", "owner"]

        self.enable_basic_rate_limit = enable_basic_rate_limit
        self.max_login_attempts = max_login_attempts
        self.login_block_minutes = login_block_minutes
        self._login_attempts: dict[str, dict[str, object]] = {}


    def check_login_allowed(self, key: str) -> bool:
        """
        Возвращает False, если для данного ключа (обычно IP) действует блокировка.
        """
        if not self.enable_basic_rate_limit:
            return True

        now = datetime.now(timezone.utc)
        entry = self._login_attempts.get(key)
        if not entry:
            return True

        blocked_until = entry.get("blocked_until")
        if isinstance(blocked_until, datetime) and blocked_until > now:
            return False

        return True

    def register_login_failure(self, key: str) -> None:
        if not self.enable_basic_rate_limit:
            return

        now = datetime.now(timezone.utc)
        entry = self._login_attempts.get(key) or {"fails": 0, "blocked_until": None}

        blocked_until = entry.get("blocked_until")
        if isinstance(blocked_until, datetime) and blocked_until > now:
            self._login_attempts[key] = entry
            return

        fails = int(entry.get("fails", 0)) + 1
        if fails >= self.max_login_attempts:
            entry["fails"] = 0
            entry["blocked_until"] = now + timedelta(minutes=self.login_block_minutes)
        else:
            entry["fails"] = fails
            entry["blocked_until"] = None

        self._login_attempts[key] = entry

    def register_login_success(self, key: str) -> None:
        if not self.enable_basic_rate_limit:
            return
        self._login_attempts.pop(key, None)


    def attach(
        self,
        app: FastAPI,
        prefix: str = "/user_manager",
        enable_cors: bool = True,
        allow_origins: Optional[list[str]] = None,
        allow_credentials: bool = False,
        allow_methods: Optional[list[str]] = None,
        allow_headers: Optional[list[str]] = None,
        root_user: Optional[RootUserConfig] = None,
    ) -> None:
        """
        Подключает эндпоинты к FastAPI, включает CORS и (опционально)
        добавляет инициализацию root-пользователя через lifespan.
        """

        if enable_cors:
            origins = allow_origins or ["*"]
            methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            headers = allow_headers or ["Authorization", "Content-Type"]

            if allow_credentials and ("*" in origins or origins == ["*"]):
                logger.warning(
                    "CORS: allow_credentials=True и origins='*'. "
                    "Для продакшена задай явный список доменов."
                )

            app.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=allow_credentials,
                allow_methods=methods,
                allow_headers=headers,
            )
            logger.info(
                "UserManager CORS enabled: origins=%s, credentials=%s, methods=%s, headers=%s",
                origins,
                allow_credentials,
                methods,
                headers,
            )

        router = get_user_router(self)
        app.include_router(router, prefix=prefix)
        logger.info("UserManager routes attached under prefix '%s'", prefix)

        if root_user is not None:
            from .db_utils import ensure_root_user

            original_lifespan = app.router.lifespan_context

            @asynccontextmanager
            async def lifespan(app_: FastAPI):
                if original_lifespan is not None:
                    async with original_lifespan(app_) as state:
                        created = await ensure_root_user(
                            self,
                            login=root_user.login,
                            email=root_user.email,
                            password=root_user.password,
                        )
                        if created:
                            logger.info(
                                "Создан root-пользователь '%s' с ролями ['owner', 'admin']",
                                root_user.login,
                            )
                        else:
                            logger.info(
                                "Root-пользователь '%s' уже существует",
                                root_user.login,
                            )
                        yield state
                else:
                    created = await ensure_root_user(
                        self,
                        login=root_user.login,
                        email=root_user.email,
                        password=root_user.password,
                    )
                    if created:
                        logger.info(
                            "Создан root-пользователь '%s' с ролями ['owner', 'admin']",
                            root_user.login,
                        )
                    else:
                        logger.info(
                            "Root-пользователь '%s' уже существует",
                            root_user.login,
                        )
                    yield

            app.router.lifespan_context = lifespan
