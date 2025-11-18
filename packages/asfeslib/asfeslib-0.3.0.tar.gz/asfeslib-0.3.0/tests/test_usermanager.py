# tests/test_usermanager.py
"""
Тесты для asfeslib.fastapi.usermanager:

- init_user_manager и глобальные переменные
- ensure_root_user (идемпотентность)
- создание root-пользователя после attach()
- логин /me
- админские эндпоинты (/users, /admin_only)
- смена пароля
- базовый rate-limit по IP
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

import asfeslib.fastapi.usermanager as um
from asfeslib.fastapi.usermanager.manager import UserManager, RootUserConfig
from asfeslib.fastapi.usermanager.db_utils import ensure_root_user


class FakePGDB:
    """
    Минимальная фейковая "PostgreSQL" БД для тестов UserManager.

    Поддерживает только те запросы, которые реально используются в db_utils.py:
    - SELECT ... FROM users WHERE login = $1
    - SELECT ... FROM users
    - INSERT INTO users ...
    - UPDATE users ...
    - DELETE FROM users ...
    """

    def __init__(self) -> None:
        self.users: dict[str, dict] = {}
        self.next_id: int = 1

    async def fetchrow(self, query: str, *params):
        query = query.strip()
        if (
            query.startswith(
                "SELECT id, login, email, password_hash, roles, is_active FROM users WHERE login ="
            )
            or "FROM users WHERE login = $1" in query
        ):
            login = params[0]
            user = self.users.get(login)
            if user is None:
                return None
            return user.copy()
        raise AssertionError(f"Unexpected fetchrow query: {query!r}")

    async def fetch(self, query: str, *params):
        query = query.strip()
        if query.startswith("SELECT id, login, email, roles, is_active FROM users"):
            rows = []
            for u in self.users.values():
                row = {
                    "id": u["id"],
                    "login": u["login"],
                    "email": u["email"],
                    "roles": u["roles"],
                    "is_active": u["is_active"],
                }
                rows.append(row)
            return rows
        raise AssertionError(f"Unexpected fetch query: {query!r}")

    async def execute(self, query: str, *params):
        query = query.strip()

        # INSERT
        if query.startswith("INSERT INTO users"):
            # Все INSERT в коде имеют одинаковую сигнатуру параметров
            login, email, password_hash, roles, is_active, created_at = params
            user = {
                "id": self.next_id,
                "login": login,
                "email": email,
                "password_hash": password_hash,
                "roles": roles,
                "is_active": is_active,
                "created_at": created_at,
            }
            self.users[login] = user
            self.next_id += 1
            return "INSERT 0 1"

        # UPDATE email / roles / is_active
        if query.startswith("UPDATE users") and "SET email =" in query:
            login, email, roles, is_active = params
            user = self.users.get(login)
            if user:
                user["email"] = email
                user["roles"] = roles
                user["is_active"] = is_active
            return "UPDATE 1"

        # UPDATE password_hash
        if query.startswith("UPDATE users") and "SET password_hash" in query:
            login, hashed = params
            user = self.users.get(login)
            if user:
                user["password_hash"] = hashed
            return "UPDATE 1"

        # DELETE
        if query.startswith("DELETE FROM users WHERE login"):
            login = params[0]
            self.users.pop(login, None)
            return "DELETE 1"

        raise AssertionError(f"Unexpected execute query: {query!r}")


@pytest.fixture
def app_and_manager():
    """
    Создаёт FastAPI + UserManager + FakePGDB.

    Важно:
    - db_type='PostgreSQL'
    - включён базовый rate-limit по IP
    - root_user передаётся в attach, но в тестах мы дополнительно вызываем ensure_root_user()
      напрямую, чтобы не зависеть от поведения lifespan в httpx.
    """
    db = FakePGDB()
    root_cfg = RootUserConfig(
        login="root",
        email="root@example.com",
        password="rootpass123",
    )

    manager = UserManager(
        db_type="PostgreSQL",
        db=db,
        jwt_secret_key="super-secret-key-that-is-long-enough-123456",
        jwt_algorithm="HS256",
        access_token_ttl=15,
        refresh_token_ttl=60 * 24,
        allowed_roles=None,
        enable_basic_rate_limit=True,
        max_login_attempts=3,
        login_block_minutes=10,
    )

    app = FastAPI()
    manager.attach(app, root_user=root_cfg)

    return app, manager, db, root_cfg


# -----------------------------------------------------------------------------
# init_user_manager и глобальные переменные
# -----------------------------------------------------------------------------


def test_init_user_manager_sets_globals_and_returns_manager():
    fake_db = object()

    manager = um.init_user_manager(
        db_type="PostgreSQL",
        db=fake_db,
        jwt_secret_key="x" * 32,
    )

    assert isinstance(manager, UserManager)
    assert manager.db is fake_db
    # Проверяем, что глобалы в модуле были заполнены
    assert um.bd is fake_db
    assert um.bd_type == "PostgreSQL"
    assert um.JWT_SECRET_KEY == "x" * 32


# -----------------------------------------------------------------------------
# ensure_root_user — идемпотентность
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ensure_root_user_idempotent():
    db = FakePGDB()
    manager = UserManager(
        db_type="PostgreSQL",
        db=db,
        jwt_secret_key="y" * 32,
    )

    created_first = await ensure_root_user(
        manager,
        login="root",
        email="root@example.com",
        password="secret123",
    )
    created_second = await ensure_root_user(
        manager,
        login="root",
        email="root@example.com",
        password="secret123",
    )

    assert created_first is True
    assert created_second is False
    assert "root" in db.users
    user = db.users["root"]
    assert "owner" in user["roles"]
    assert "admin" in user["roles"]


# -----------------------------------------------------------------------------
# Root-пользователь можно создать после attach()
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_root_user_can_be_initialized_after_attach(app_and_manager):
    app, manager, db, root_cfg = app_and_manager

    # До явного ensure_root_user — root'а нет
    assert root_cfg.login not in db.users

    created = await ensure_root_user(
        manager,
        login=root_cfg.login,
        email=root_cfg.email,
        password=root_cfg.password,
    )
    assert created is True
    assert root_cfg.login in db.users
    user = db.users[root_cfg.login]
    assert "owner" in user["roles"]
    assert "admin" in user["roles"]


# -----------------------------------------------------------------------------
# Логин и /me
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_success_and_me_returns_correct_user(app_and_manager):
    app, manager, db, root_cfg = app_and_manager

    # гарантируем, что root создан
    await ensure_root_user(
        manager,
        login=root_cfg.login,
        email=root_cfg.email,
        password=root_cfg.password,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Логинимся root-пользователем
        resp = await client.post(
            "/user_manager/login",
            json={"login": root_cfg.login, "password": root_cfg.password},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "access_token" in data
        access = data["access_token"]

        # Проверяем /me
        me_resp = await client.get(
            "/user_manager/me",
            headers={"Authorization": f"Bearer {access}"},
        )
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["login"] == root_cfg.login
        assert "owner" in me_data["roles"]
        assert "admin" in me_data["roles"]


# -----------------------------------------------------------------------------
# Админские эндпоинты: создание пользователя, список пользователей, роли
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_admin_can_create_and_list_users_and_password_not_exposed(app_and_manager):
    app, manager, db, root_cfg = app_and_manager

    # гарантируем, что root создан
    await ensure_root_user(
        manager,
        login=root_cfg.login,
        email=root_cfg.email,
        password=root_cfg.password,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Логинимся как root (admin/owner)
        login_resp = await client.post(
            "/user_manager/login",
            json={"login": root_cfg.login, "password": root_cfg.password},
        )
        assert login_resp.status_code == 200
        admin_access = login_resp.json()["access_token"]

        # Создаём обычного пользователя
        user_payload = {
            "login": "user1",
            "email": "user1@example.com",
            "password": "userpass123",
            "roles": ["user"],
            "is_active": True,
        }
        create_resp = await client.post(
            "/user_manager/users",
            json=user_payload,
            headers={"Authorization": f"Bearer {admin_access}"},
        )
        assert create_resp.status_code == 201
        created = create_resp.json()["user"]
        assert created["login"] == "user1"
        assert created["roles"] == ["user"]

        # Список пользователей
        list_resp = await client.get(
            "/user_manager/users",
            headers={"Authorization": f"Bearer {admin_access}"},
        )
        assert list_resp.status_code == 200
        list_data = list_resp.json()
        assert list_data["status"] == "ok"
        users = list_data["users"]

        u = next(u for u in users if u["login"] == "user1")
        # Не должно быть password_hash в публичной схеме
        assert "password_hash" not in u
        assert u["email"] == "user1@example.com"


@pytest.mark.asyncio
async def test_non_admin_cannot_access_admin_only(app_and_manager):
    app, manager, db, root_cfg = app_and_manager

    # гарантируем, что root создан
    await ensure_root_user(
        manager,
        login=root_cfg.login,
        email=root_cfg.email,
        password=root_cfg.password,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Логинимся как root (чтобы создать обычного пользователя)
        login_resp = await client.post(
            "/user_manager/login",
            json={"login": root_cfg.login, "password": root_cfg.password},
        )
        assert login_resp.status_code == 200
        admin_access = login_resp.json()["access_token"]

        # Создаём пользователя с ролью только "user"
        user_payload = {
            "login": "plainuser",
            "email": "plain@example.com",
            "password": "plainpass123",
            "roles": ["user"],
            "is_active": True,
        }
        create_resp = await client.post(
            "/user_manager/users",
            json=user_payload,
            headers={"Authorization": f"Bearer {admin_access}"},
        )
        assert create_resp.status_code == 201

        # Логинимся как plainuser
        user_login_resp = await client.post(
            "/user_manager/login",
            json={"login": "plainuser", "password": "plainpass123"},
        )
        assert user_login_resp.status_code == 200
        user_access = user_login_resp.json()["access_token"]

        # Пытаемся обратиться к /admin_only
        admin_only_resp = await client.get(
            "/user_manager/admin_only",
            headers={"Authorization": f"Bearer {user_access}"},
        )
        assert admin_only_resp.status_code == 403
        assert admin_only_resp.json()["detail"].startswith("Требуется роль")


# -----------------------------------------------------------------------------
# Логин: неизвестный пользователь — 401 без лишней информации
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_unknown_user_returns_401(app_and_manager):
    app, manager, db, root_cfg = app_and_manager

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/user_manager/login",
            json={"login": "nonexistent_user", "password": "whatever123"},
        )
        assert resp.status_code == 401
        body = resp.json()
        # Сообщение общее, без раскрытия "логин не существует"
        assert body["detail"] == "Неверный логин или пароль"


# -----------------------------------------------------------------------------
# Смена пароля: после смены старый пароль не работает, новый — работает
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_change_password_allows_new_password(app_and_manager):
    app, manager, db, root_cfg = app_and_manager

    # гарантируем, что root создан
    await ensure_root_user(
        manager,
        login=root_cfg.login,
        email=root_cfg.email,
        password=root_cfg.password,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Логинимся root
        login_resp = await client.post(
            "/user_manager/login",
            json={"login": root_cfg.login, "password": root_cfg.password},
        )
        assert login_resp.status_code == 200
        access = login_resp.json()["access_token"]

        new_password = "new_root_password_456"

        # Меняем пароль root через админский эндпоинт
        change_resp = await client.post(
            f"/user_manager/users/{root_cfg.login}/password",
            json={"password": new_password},
            headers={"Authorization": f"Bearer {access}"},
        )
        assert change_resp.status_code == 200

        # Логин со старым паролем — должен провалиться
        old_login_resp = await client.post(
            "/user_manager/login",
            json={"login": root_cfg.login, "password": root_cfg.password},
        )
        assert old_login_resp.status_code == 401

        # Логин с новым паролем — должен пройти
        new_login_resp = await client.post(
            "/user_manager/login",
            json={"login": root_cfg.login, "password": new_password},
        )
        assert new_login_resp.status_code == 200
        assert "access_token" in new_login_resp.json()


# -----------------------------------------------------------------------------
# Rate limit: блокировка после нескольких неудачных попыток
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rate_limit_blocks_after_too_many_failures(app_and_manager):
    app, manager, db, root_cfg = app_and_manager

    # гарантируем, что root создан
    await ensure_root_user(
        manager,
        login=root_cfg.login,
        email=root_cfg.email,
        password=root_cfg.password,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Несколько раз подряд пытаемся залогиниться с неверным паролем
        for _ in range(manager.max_login_attempts):
            resp = await client.post(
                "/user_manager/login",
                json={"login": root_cfg.login, "password": "wrong_password_123"},
            )
            # Пока лимит не сработал — будет 401/403
            assert resp.status_code in (401, 403)

        # Следующая попытка должна получить 429
        blocked_resp = await client.post(
            "/user_manager/login",
            json={"login": root_cfg.login, "password": "wrong_password_123"},
        )
        assert blocked_resp.status_code == 429
        assert "Слишком много попыток" in blocked_resp.json()["detail"]


# -----------------------------------------------------------------------------
# Rate limit: логика блокировки/сброса без HTTP (чисто методы UserManager)
# -----------------------------------------------------------------------------


def test_rate_limit_logic_blocks_and_resets():
    db = FakePGDB()
    manager = UserManager(
        db_type="PostgreSQL",
        db=db,
        jwt_secret_key="z" * 32,
        enable_basic_rate_limit=True,
        max_login_attempts=2,
        login_block_minutes=10,
    )

    key = "127.0.0.1"

    # Изначально запросы разрешены
    assert manager.check_login_allowed(key) is True

    # После одной неудачи всё ещё можно пробовать
    manager.register_login_failure(key)
    assert manager.check_login_allowed(key) is True

    # После второй — блокировка
    manager.register_login_failure(key)
    assert manager.check_login_allowed(key) is False

    # Успешный логин сбрасывает блокировку
    manager.register_login_success(key)
    assert manager.check_login_allowed(key) is True
