from typing import Optional, Tuple
from urllib.parse import urlsplit, quote_plus

import psycopg
from psycopg import AsyncConnection
from pydantic import BaseModel, Field
from asfeslib.core.logger import Logger

logger = Logger(name=__name__)


class PostgresConnectScheme(BaseModel):
    db_url: Optional[str] = Field(
        default=None,
        description="Полная ссылка подключения (например, postgresql://user:pass@host:port/db)",
    )
    host: str = Field(default="localhost", description="Хост PostgreSQL")
    port: int = Field(default=5432, description="Порт PostgreSQL")
    username: str = Field(default="postgres", description="Имя пользователя")
    password: Optional[str] = Field(default=None, description="Пароль")
    db_name: str = Field(default="hackathon_db", description="Имя базы данных")

    def assemble_url(self) -> str:
        """
        Собрать URI вида postgresql://user:pass@host:port/db_name.
        Если db_url указан, возвращается он как есть.
        """
        if self.db_url:
            return self.db_url
        if self.password is not None:
            auth = f"{quote_plus(self.username)}:{quote_plus(self.password)}@"
        else:
            auth = f"{quote_plus(self.username)}@"
        return f"postgresql://{auth}{self.host}:{self.port}/{self.db_name}"

    def describe_for_log(self) -> str:
        """
        Короткое описание цели подключения без паролей: host:port/db
        """
        if self.db_url:
            u = urlsplit(self.db_url)
            host = u.hostname or self.host
            port = u.port or self.port
            path = u.path.lstrip("/") if u.path else ""
            db = path.split("/", 1)[0] or self.db_name
            return f"{host}:{port}/{db}"
        return f"{self.host}:{self.port}/{self.db_name}"


async def connect_postgres(data: PostgresConnectScheme) -> Tuple[AsyncConnection, bool]:
    """
    Создаёт асинхронное подключение к PostgreSQL через psycopg3.
    Возвращает (connection, status)
    """
    conn: Optional[AsyncConnection] = None
    status = False

    dsn = data.assemble_url()
    target = data.describe_for_log()

    try:
        conn = await psycopg.AsyncConnection.connect(dsn, connect_timeout=10)

        async with conn.cursor() as cur:
            await cur.execute("SELECT 1;")
            row = await cur.fetchone()
            status = bool(row and row[0] == 1)

        if status:
            logger.info(f"Подключение к PostgreSQL установлено: {target}")
        else:
            logger.error(f"PostgreSQL не ответил корректно на SELECT 1 для {target}")

    except Exception as e:
        logger.error(f"Ошибка подключения к PostgreSQL ({target}): {e}")

    return conn, status
