from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError


class JWTManager:
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_ttl: int = 15,
        refresh_token_ttl: int = 43200,
    ):
        if not isinstance(secret_key, str) or len(secret_key) < 32:
            raise ValueError(
                "JWT secret key должен быть строкой длиной минимум 32 символа"
            )

        if access_token_ttl <= 0 or refresh_token_ttl <= 0:
            raise ValueError("TTL для токенов должен быть положительным числом минут")

        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_ttl = access_token_ttl
        self.refresh_token_ttl = refresh_token_ttl

    def encode(self, data: dict, ttl_min: int) -> str:
        payload = data.copy()
        now = datetime.now(timezone.utc)
        payload["exp"] = now + timedelta(minutes=ttl_min)
        payload["iat"] = now
        payload["token_type"] = "JWT"
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_access_token(self, data: dict) -> str:
        return self.encode(data, self.access_token_ttl)

    def create_refresh_token(self, data: dict) -> str:
        return self.encode(data, self.refresh_token_ttl)

    def decode(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            raise ValueError("Invalid token")
