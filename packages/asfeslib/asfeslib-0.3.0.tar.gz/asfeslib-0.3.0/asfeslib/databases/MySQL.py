from typing import Optional, Tuple
from urllib.parse import urlsplit, quote_plus

import aiomysql
from pydantic import BaseModel, Field
from asfeslib.core.logger import Logger

logger = Logger(name=__name__)


class MariaConnectScheme(BaseModel):
    db_url: Optional[str] = Field(
        default=None,
        description="Полная ссылка подключения (например, mysql://user:pass@host:port/db)",
    )
    host: str = Field(default="localhost", description="Хост базы данных")
    port: int = Field(default=3306, description="Порт MariaDB/MySQL")
    username: str = Field(default="root", description="Имя пользователя")
    password: Optional[str] = Field(default=None, description="Пароль пользователя")
    db_name: str = Field(default="hackathon_db", description="Имя базы данных")

    def assemble_url(self) -> str:
        """
        Собрать URI вида mysql://user:pass@host:port/db_name.

        Сейчас используется для отладки и тестов.
        """
        if self.db_url:
            return self.db_url
        if self.password is not None:
            auth = f"{quote_plus(self.username)}:{quote_plus(self.password)}@"
        else:
            auth = f"{quote_plus(self.username)}@"
        return f"mysql://{auth}{self.host}:{self.port}/{self.db_name}"

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

    def resolved_connect_params(self) -> Tuple[str, int, str, Optional[str], str]:
        """
        Параметры для aiomysql.connect: (host, port, user, password, db).

        Если db_url задан, приоритет у значений из URL.
        """
        host = self.host
        port = self.port
        user = self.username
        password = self.password
        db_name = self.db_name

        if self.db_url:
            u = urlsplit(self.db_url)
            if u.hostname:
                host = u.hostname
            if u.port:
                port = u.port
            if u.username:
                user = u.username
            if u.password:
                password = u.password
            if u.path and u.path != "/":
                name = u.path.lstrip("/").split("/", 1)[0]
                if name:
                    db_name = name

        return host, port, user, password, db_name


async def connect_mariadb(data: MariaConnectScheme) -> Tuple[aiomysql.Connection, bool]:
    """
    Создаёт асинхронное подключение к MariaDB через aiomysql.
    Возвращает (connection, status)
    """
    conn: Optional[aiomysql.Connection] = None
    status = False

    host, port, user, password, db_name = data.resolved_connect_params()
    target = data.describe_for_log()

    try:
        conn = await aiomysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db_name,
            autocommit=True,
            connect_timeout=10,
        )

        async with conn.cursor() as cur:
            await cur.execute("SELECT 1;")
            result = await cur.fetchone()
            status = bool(result and result[0] == 1)

        if status:
            logger.info(f"Подключение к MariaDB установлено: {target}")
        else:
            logger.error(f"MariaDB не ответила корректно на SELECT 1 для {target}")

    except Exception as e:
        logger.error(f"Ошибка подключения к MariaDB ({target}): {e}")

    return conn, status