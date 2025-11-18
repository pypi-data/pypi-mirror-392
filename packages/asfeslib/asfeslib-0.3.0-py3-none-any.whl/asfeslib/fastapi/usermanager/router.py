from __future__ import annotations

from typing import TYPE_CHECKING, List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse

from .schemas import (
    LoginForm,
    RegistrationForm,
    UserInToken,
    TokenResponse,
    RegistrationResponse,
    UserPublic,
    UserDetailResponse,
    UsersListResponse,
    AdminCreateUser,
    AdminUpdateUser,
    AdminChangePassword,
)
from .deps import get_current_user, require_role
from .security_password import verify_password
from .db_utils import (
    manager_get_user,
    manager_register_user,
    manager_list_users,
    manager_create_user,
    manager_update_user,
    manager_delete_user,
    manager_change_password,
)

if TYPE_CHECKING:
    from .manager import UserManager


def _to_public_user(raw: dict) -> UserPublic:
    return UserPublic(
        id=str(raw["id"]),
        login=raw["login"],
        email=raw["email"],
        roles=raw.get("roles", []),
        is_active=raw.get("is_active", True),
    )


def get_user_router(manager: "UserManager") -> APIRouter:
    router = APIRouter()

    @router.post(
        "/login",
        response_model=TokenResponse,
        status_code=status.HTTP_200_OK,
        summary="Логин по логину и паролю",
    )
    async def login(form: LoginForm, request: Request):
        client_ip = request.client.host if request.client else "unknown"

        if getattr(manager, "enable_basic_rate_limit", False):
            if not manager.check_login_allowed(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Слишком много попыток входа, попробуйте позже",
                )

        user = await manager_get_user(manager, form.login)
        if not user:
            if getattr(manager, "enable_basic_rate_limit", False):
                manager.register_login_failure(client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
            )

        if not user.get("is_active", True):
            if getattr(manager, "enable_basic_rate_limit", False):
                manager.register_login_failure(client_ip)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь заблокирован",
            )

        if not verify_password(
            form.password.get_secret_value(),
            user["password_hash"],
        ):
            if getattr(manager, "enable_basic_rate_limit", False):
                manager.register_login_failure(client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
            )

        if getattr(manager, "enable_basic_rate_limit", False):
            manager.register_login_success(client_ip)

        roles = user.get("roles", [])
        roles = [r for r in roles if r in manager.allowed_roles]

        access = manager.jwt.create_access_token(
            {
                "sub": str(user["id"]),
                "login": user["login"],
                "roles": roles,
            }
        )

        refresh = manager.jwt.create_refresh_token(
            {
                "sub": str(user["id"]),
            }
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ok",
                "access_token": access,
                "refresh_token": refresh,
                "token_type": "bearer",
            },
        )

    @router.post(
        "/registration",
        response_model=RegistrationResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Регистрация нового пользователя",
    )
    async def registration(form: RegistrationForm):
        try:
            await manager_register_user(manager, form)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"status": "ok"},
        )

    @router.get(
        "/me",
        response_model=UserInToken,
        status_code=status.HTTP_200_OK,
        summary="Информация о текущем пользователе",
    )
    async def me(user: UserInToken = Depends(get_current_user(manager))):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=user.dict(),
        )

    @router.get(
        "/admin_only",
        status_code=status.HTTP_200_OK,
        summary="Только для админов (тестовый эндпоинт)",
    )
    async def admin(user: UserInToken = Depends(require_role(manager, "admin"))):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "hello": user.login},
        )

    @router.get(
        "/users",
        response_model=UsersListResponse,
        status_code=status.HTTP_200_OK,
        summary="Список всех пользователей (админ)",
    )
    async def list_users(
        _: UserInToken = Depends(require_role(manager, "admin")),
    ):
        users_raw = await manager_list_users(manager)
        users_public = [_to_public_user(u).dict() for u in users_raw]
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "users": users_public},
        )

    @router.get(
        "/users/{login}",
        response_model=UserDetailResponse,
        status_code=status.HTTP_200_OK,
        summary="Получить пользователя по логину (админ)",
    )
    async def get_user(
        login: str,
        _: UserInToken = Depends(require_role(manager, "admin")),
    ):
        user = await manager_get_user(manager, login)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        public = _to_public_user(user)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "user": public.dict()},
        )

    @router.post(
        "/users",
        response_model=UserDetailResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Создать пользователя (админ)",
    )
    async def create_user(
        payload: AdminCreateUser,
        _: UserInToken = Depends(require_role(manager, "admin")),
    ):
        roles = payload.roles or ["user"]
        roles = [r for r in roles if r in manager.allowed_roles]
        if not roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Список ролей пуст или содержит только запрещённые роли",
            )

        try:
            user = await manager_create_user(
                manager=manager,
                login=payload.login,
                email=payload.email,
                password=payload.password.get_secret_value(),
                roles=roles,
                is_active=payload.is_active,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        public = _to_public_user(user)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"status": "ok", "user": public.dict()},
        )

    @router.put(
        "/users/{login}",
        response_model=UserDetailResponse,
        status_code=status.HTTP_200_OK,
        summary="Обновить пользователя (админ)",
    )
    async def update_user(
        login: str,
        payload: AdminUpdateUser,
        _: UserInToken = Depends(require_role(manager, "admin")),
    ):
        user = await manager_get_user(manager, login)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        roles = payload.roles
        if roles is not None:
            roles = [r for r in roles if r in manager.allowed_roles]
            if not roles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Список ролей пуст или содержит только запрещённые роли",
                )

        updated = await manager_update_user(
            manager=manager,
            login=login,
            email=payload.email,
            roles=roles,
            is_active=payload.is_active,
        )

        public = _to_public_user(updated)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "user": public.dict()},
        )

    @router.delete(
        "/users/{login}",
        status_code=status.HTTP_200_OK,
        summary="Удалить пользователя (админ)",
    )
    async def delete_user(
        login: str,
        _: UserInToken = Depends(require_role(manager, "admin")),
    ):
        user = await manager_get_user(manager, login)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        await manager_delete_user(manager, login)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok"},
        )

    @router.post(
        "/users/{login}/password",
        status_code=status.HTTP_200_OK,
        summary="Сменить пароль пользователю (админ)",
    )
    async def change_password(
        login: str,
        payload: AdminChangePassword,
        _: UserInToken = Depends(require_role(manager, "admin")),
    ):
        user = await manager_get_user(manager, login)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        await manager_change_password(
            manager=manager,
            login=login,
            new_password=payload.password.get_secret_value(),
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok"},
        )

    return router
