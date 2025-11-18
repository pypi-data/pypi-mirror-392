from typing import List, Any, Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict, SecretStr


class LoginForm(BaseModel):
    login: str = Field(..., min_length=3, max_length=64)
    password: SecretStr = Field(..., min_length=6)


class RegistrationForm(BaseModel):
    login: str = Field(..., min_length=3, max_length=64)
    email: EmailStr = Field(...)

    password: SecretStr = Field(..., min_length=6)
    password_repeat: SecretStr = Field(..., min_length=6)


class UserInToken(BaseModel):
    id: Any
    login: str
    roles: List[str]


class TokenResponse(BaseModel):
    status: str = "ok"
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegistrationResponse(BaseModel):
    status: str = "ok"


class ErrorResponse(BaseModel):
    status: str = "error"
    detail: str



class DBUser(BaseModel):
    """
    Внутренний объект, используемый после получения данных из БД.
    Это НЕ схема API.
    """

    id: Any
    login: str
    email: EmailStr
    password_hash: str
    roles: List[str] = Field(default_factory=lambda: ["user"])
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class UserPublic(BaseModel):
    """Публичное представление пользователя без пароля."""
    id: Any
    login: str
    email: EmailStr
    roles: List[str]
    is_active: bool = True


class UsersListResponse(BaseModel):
    status: str = "ok"
    users: List[UserPublic]


class UserDetailResponse(BaseModel):
    status: str = "ok"
    user: UserPublic


class AdminCreateUser(BaseModel):
    """Создание пользователя админом."""
    login: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: SecretStr = Field(..., min_length=6)
    roles: List[str] = Field(default_factory=lambda: ["user"])
    is_active: bool = True


class AdminUpdateUser(BaseModel):
    """Частичное обновление пользователя."""
    email: Optional[EmailStr] = None
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None


class AdminChangePassword(BaseModel):
    """Смена пароля пользователю (админская)."""
    password: SecretStr = Field(..., min_length=6)
