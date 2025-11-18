from typing import Any, Dict, Optional, TYPE_CHECKING, List

from asfeslib.core.utils import now_str

from .schemas import RegistrationForm
from .security_password import hash_password

if TYPE_CHECKING:
    from .manager import UserManager


async def manager_get_user(manager: "UserManager", login: str) -> Optional[Dict[str, Any]]:
    db = manager.db
    db_type = manager.db_type

    if db_type == "MongoDB":
        users = db["users"]
        data = await users.find_one({"login": login})
        if not data:
            return None
        data["id"] = str(data["_id"])
        return normalize_mongo_user(data)

    if db_type == "PostgreSQL":
        row = await db.fetchrow(
            "SELECT id, login, email, password_hash, roles, is_active FROM users WHERE login = $1",
            login,
        )
        return normalize_pg_user(row) if row else None

    if db_type == "MySQL":
        row = await db.fetchrow(
            "SELECT id, login, email, password_hash, roles, is_active FROM users WHERE login = %s",
            (login,),
        )
        return normalize_mysql_user(row) if row else None

    raise RuntimeError("Unknown DB type")


async def manager_register_user(manager: "UserManager", form: RegistrationForm) -> None:
    db = manager.db
    db_type = manager.db_type

    if form.password.get_secret_value() != form.password_repeat.get_secret_value():
        raise ValueError("Пароли не совпадают")

    existing = await manager_get_user(manager, form.login)
    if existing:
        raise ValueError("Пользователь с таким логином уже существует")

    password_hash = hash_password(form.password.get_secret_value())

    if db_type == "MongoDB":
        users = db["users"]
        await users.insert_one(
            {
                "login": form.login,
                "email": form.email,
                "password_hash": password_hash,
                "roles": ["user"],
                "is_active": True,
                "created_at": now_str(),
            }
        )
        return

    if db_type == "PostgreSQL":
        await db.execute(
            """
            INSERT INTO users (login, email, password_hash, roles, is_active, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            form.login,
            form.email,
            password_hash,
            ["user"],
            True,
            now_str(),
        )
        return

    if db_type == "MySQL":
        await db.execute(
            """
            INSERT INTO users (login, email, password_hash, roles, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                form.login,
                form.email,
                password_hash,
                "user",
                True,
                now_str(),
            ),
        )
        return

    raise RuntimeError("Unsupported DB type")


async def manager_list_users(manager: "UserManager") -> List[Dict[str, Any]]:
    """Получить список всех пользователей (для админского UI)."""
    db = manager.db
    db_type = manager.db_type

    if db_type == "MongoDB":
        users_collection = db["users"]
        cursor = users_collection.find({})
        users: List[Dict[str, Any]] = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            users.append(normalize_mongo_user(doc))
        return users

    if db_type == "PostgreSQL":
        rows = await db.fetch(
            "SELECT id, login, email, roles, is_active FROM users"
        )
        return [normalize_pg_user(row) for row in rows]

    if db_type == "MySQL":
        rows = await db.fetch(
            "SELECT id, login, email, roles, is_active FROM users"
        )
        return [normalize_mysql_user(row) for row in rows]

    raise RuntimeError("Unsupported DB type")


async def manager_create_user(
    manager: "UserManager",
    login: str,
    email: str,
    password: str,
    roles: Optional[List[str]] = None,
    is_active: bool = True,
) -> Dict[str, Any]:
    """Создание пользователя админом."""
    db = manager.db
    db_type = manager.db_type

    existing = await manager_get_user(manager, login)
    if existing:
        raise ValueError("Пользователь с таким логином уже существует")

    roles = roles or ["user"]
    password_hash = hash_password(password)
    now = now_str()

    if db_type == "MongoDB":
        users = db["users"]
        await users.insert_one(
            {
                "login": login,
                "email": email,
                "password_hash": password_hash,
                "roles": roles,
                "is_active": is_active,
                "created_at": now,
            }
        )
        doc = await users.find_one({"login": login})
        doc["id"] = str(doc["_id"])
        return normalize_mongo_user(doc)

    if db_type == "PostgreSQL":
        await db.execute(
            """
            INSERT INTO users (login, email, password_hash, roles, is_active, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            login,
            email,
            password_hash,
            roles,
            is_active,
            now,
        )
        row = await db.fetchrow(
            "SELECT id, login, email, password_hash, roles, is_active FROM users WHERE login = $1",
            login,
        )
        return normalize_pg_user(row)

    if db_type == "MySQL":
        await db.execute(
            """
            INSERT INTO users (login, email, password_hash, roles, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                login,
                email,
                password_hash,
                ",".join(roles),
                is_active,
                now,
            ),
        )
        row = await db.fetchrow(
            "SELECT id, login, email, password_hash, roles, is_active FROM users WHERE login = %s",
            (login,),
        )
        return normalize_mysql_user(row)

    raise RuntimeError("Unsupported DB type")


async def manager_update_user(
    manager: "UserManager",
    login: str,
    email: Optional[str] = None,
    roles: Optional[List[str]] = None,
    is_active: Optional[bool] = None,
) -> Dict[str, Any]:
    """Частичное обновление пользователя (email/roles/is_active)."""
    existing = await manager_get_user(manager, login)
    if not existing:
        raise ValueError("Пользователь не найден")

    new_email = email if email is not None else existing["email"]
    new_roles = roles if roles is not None else existing.get("roles", ["user"])
    new_is_active = is_active if is_active is not None else existing.get("is_active", True)

    db = manager.db
    db_type = manager.db_type

    if db_type == "MongoDB":
        users = db["users"]
        await users.update_one(
            {"login": login},
            {
                "$set": {
                    "email": new_email,
                    "roles": new_roles,
                    "is_active": new_is_active,
                }
            },
        )
        doc = await users.find_one({"login": login})
        doc["id"] = str(doc["_id"])
        return normalize_mongo_user(doc)

    if db_type == "PostgreSQL":
        await db.execute(
            """
            UPDATE users
               SET email = $2,
                   roles = $3,
                   is_active = $4
             WHERE login = $1
            """,
            login,
            new_email,
            new_roles,
            new_is_active,
        )
        row = await db.fetchrow(
            "SELECT id, login, email, password_hash, roles, is_active FROM users WHERE login = $1",
            login,
        )
        return normalize_pg_user(row)

    if db_type == "MySQL":
        await db.execute(
            """
            UPDATE users
               SET email = %s,
                   roles = %s,
                   is_active = %s
             WHERE login = %s
            """,
            (
                new_email,
                ",".join(new_roles),
                new_is_active,
                login,
            ),
        )
        row = await db.fetchrow(
            "SELECT id, login, email, password_hash, roles, is_active FROM users WHERE login = %s",
            (login,),
        )
        return normalize_mysql_user(row)

    raise RuntimeError("Unsupported DB type")


async def manager_delete_user(manager: "UserManager", login: str) -> None:
    """Удаление пользователя по логину."""
    db = manager.db
    db_type = manager.db_type

    if db_type == "MongoDB":
        users = db["users"]
        await users.delete_one({"login": login})
        return

    if db_type == "PostgreSQL":
        await db.execute("DELETE FROM users WHERE login = $1", login)
        return

    if db_type == "MySQL":
        await db.execute("DELETE FROM users WHERE login = %s", (login,))
        return

    raise RuntimeError("Unsupported DB type")


async def manager_change_password(
    manager: "UserManager",
    login: str,
    new_password: str,
) -> None:
    """Смена пароля пользователю."""
    db = manager.db
    db_type = manager.db_type
    hashed = hash_password(new_password)

    if db_type == "MongoDB":
        users = db["users"]
        await users.update_one(
            {"login": login},
            {"$set": {"password_hash": hashed}},
        )
        return

    if db_type == "PostgreSQL":
        await db.execute(
            "UPDATE users SET password_hash = $2 WHERE login = $1",
            login,
            hashed,
        )
        return

    if db_type == "MySQL":
        await db.execute(
            "UPDATE users SET password_hash = %s WHERE login = %s",
            (hashed, login),
        )
        return

    raise RuntimeError("Unsupported DB type")


async def ensure_root_user(
    manager: "UserManager",
    login: str,
    email: str,
    password: str,
    roles: Optional[List[str]] = None,
) -> bool:
    """
    Инициализация root-пользователя.

    Возвращает:
        True  — если пользователь был создан,
        False — если пользователь уже существовал.
    """
    db = manager.db
    db_type = manager.db_type

    existing = await manager_get_user(manager, login)
    if existing:
        return False

    roles = roles or ["owner", "admin"]
    password_hash = hash_password(password)
    now = now_str()

    if db_type == "MongoDB":
        users = db["users"]
        await users.insert_one(
            {
                "login": login,
                "email": email,
                "password_hash": password_hash,
                "roles": roles,
                "is_active": True,
                "created_at": now,
            }
        )
        return True

    if db_type == "PostgreSQL":
        await db.execute(
            """
            INSERT INTO users (login, email, password_hash, roles, is_active, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            login,
            email,
            password_hash,
            roles,
            True,
            now,
        )
        return True

    if db_type == "MySQL":
        await db.execute(
            """
            INSERT INTO users (login, email, password_hash, roles, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                login,
                email,
                password_hash,
                ",".join(roles),
                True,
                now,
            ),
        )
        return True

    raise RuntimeError("Unsupported DB type")


def normalize_pg_user(row) -> Dict[str, Any]:
    data = dict(row)
    if isinstance(data.get("roles"), str):
        data["roles"] = [r.strip() for r in data["roles"].split(",")]
    return data


def normalize_mysql_user(row) -> Dict[str, Any]:
    data = dict(row)
    if isinstance(data.get("roles"), str):
        data["roles"] = [r.strip() for r in data["roles"].split(",")]
    return data


def normalize_mongo_user(data: dict) -> dict:
    if isinstance(data.get("roles"), str):
        data["roles"] = [r.strip() for r in data["roles"].split(",")]
    return data
