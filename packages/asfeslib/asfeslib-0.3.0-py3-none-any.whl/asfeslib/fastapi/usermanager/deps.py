from typing import TYPE_CHECKING

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .schemas import UserInToken
from .db_utils import manager_get_user

if TYPE_CHECKING:
    from .manager import UserManager

oauth2 = OAuth2PasswordBearer(tokenUrl="/user_manager/login")


def get_current_user(manager: "UserManager"):
    async def dependency(token: str = Depends(oauth2)):
        try:
            payload = manager.jwt.decode(token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен",
            )

        login = payload.get("login")
        if not login:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен",
            )

        user = await manager_get_user(manager, login)
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден или неактивен",
            )

        roles = user.get("roles", [])
        roles = [r for r in roles if r in manager.allowed_roles]

        return UserInToken(
            id=str(user["id"]),
            login=user["login"],
            roles=roles,
        )

    return dependency


def require_role(manager: "UserManager", role: str):
    def dependency(user: UserInToken = Depends(get_current_user(manager))):
        if role not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется роль {role}",
            )
        return user

    return dependency