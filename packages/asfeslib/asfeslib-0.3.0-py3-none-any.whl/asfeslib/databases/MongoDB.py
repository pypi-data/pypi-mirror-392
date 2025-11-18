from typing import Optional, Tuple
from urllib.parse import urlsplit, quote_plus

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, AnyUrl, Field
from asfeslib.core.logger import Logger

logger = Logger(name=__name__)


class MongoConnectScheme(BaseModel):
    db_url: Optional[AnyUrl] = Field(
        default=None,
        description="Полная ссылка подключения MongoDB (например, mongodb://user:pass@host:port/db)",
    )

    host: str = Field(default="localhost", description="Хост MongoDB")
    port: int = Field(default=27017, description="Порт MongoDB")
    username: Optional[str] = Field(default=None, description="Имя пользователя")
    password: Optional[str] = Field(default=None, description="Пароль")
    db_name: str = Field(default="hackathon_db", description="Имя базы данных")

    def assemble_url(self) -> str:
        """
        Собрать URI для подключения к MongoDB.

        Если db_url указан, он используется как есть.
        Иначе: mongodb://[user:pass@]host:port/db_name
        """
        if self.db_url:
            return str(self.db_url)

        auth = ""
        if self.username and self.password:
            auth = f"{quote_plus(self.username)}:{quote_plus(self.password)}@"

        return f"mongodb://{auth}{self.host}:{self.port}/{self.db_name}"

    def describe_for_log(self) -> str:
        """
        Краткое описание соединения без паролей: host:port/db
        """
        if self.db_url:
            u = urlsplit(str(self.db_url))
            host = u.hostname or self.host
            port = u.port or self.port
            path = u.path.lstrip("/") if u.path else ""
            db = path.split("/", 1)[0] or self.db_name
            return f"{host}:{port}/{db}"
        return f"{self.host}:{self.port}/{self.db_name}"

    def resolved_db_name(self) -> str:
        """
        Имя базы, которое реально используется при подключении.
        Если db_url содержит /mydb — берём mydb, иначе db_name.
        """
        if self.db_url:
            u = urlsplit(str(self.db_url))
            if u.path and u.path != "/":
                name = u.path.lstrip("/").split("/", 1)[0]
                if name:
                    return name
        return self.db_name


async def connect_mongo(
    data: MongoConnectScheme,
) -> Tuple[AsyncIOMotorClient, AsyncIOMotorDatabase, bool]:
    """
    Создаёт асинхронное подключение к MongoDB через Motor.
    Принимает либо готовый db_url, либо отдельные поля.
    Возвращает (клиент, база данных, статус подключения).
    """
    mongo_uri = data.assemble_url()
    client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)

    db_name = data.resolved_db_name()
    db = client[db_name]
    status = False

    target = data.describe_for_log()

    try:
        result = await client.admin.command("ping")
        status = result.get("ok", 0) == 1.0
        if status:
            logger.info(f"Подключение к MongoDB установлено: {target}")
        else:
            logger.error(f"MongoDB вернул некорректный ответ на ping для {target}: {result}")
    except Exception as e:
        logger.error(f"Ошибка подключения к MongoDB ({target}): {e}")

    return client, db, status
