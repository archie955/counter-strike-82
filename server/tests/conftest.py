from collections.abc import AsyncGenerator
from typing import Any

import pytest_asyncio
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.database import get_db
from main import app
from models.user_models import Base

SQLALCHEMY_DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@localhost:5433/test_db"
)


@pytest_asyncio.fixture(scope="function")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(fn=Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(fn=Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with SessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app, raise_app_exceptions=True)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


class Helpers:
    @staticmethod
    async def register_user(client: AsyncClient) -> dict[str, str]:
        user = {
            "email": "authuser@example.com",
            "username": "authusername",
            "password": "authpassword",
        }
        response = await client.post(url="/users", json=user)

        assert response.status_code == 201
        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data
        return user

    @staticmethod
    async def full_login(client: AsyncClient) -> dict[str, str]:
        user = {
            "email": "authuser@example.com",
            "username": "authusername",
            "password": "authpassword",
        }
        user_payload = await client.post(url="/users", json=user)

        assert user_payload.status_code == 201

        response = await client.post(
            url="/users/login",
            data={"username": user["email"], "password": user["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        user["access_token"] = data["access_token"]
        return user

    @staticmethod
    def auth_headers(user: dict[str, str], expired: bool = False) -> dict[str, str]:
        token = user["access_token"]
        if expired:
            token = "expired_token"
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    async def update_user(
        client: AsyncClient, updated: dict[str, str], user: dict[str, str]
    ) -> dict[str, str]:
        response = await client.put(
            url="/users",
            json=updated,
            headers={"Authorization": f"Bearer {user['access_token']}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == updated["updated_user"]["username"]  # ty:ignore[invalid-argument-type]
        assert data["email"] == updated["updated_user"]["email"]  # ty:ignore[invalid-argument-type]

        return data


@pytest_asyncio.fixture
def helpers() -> Helpers:
    return Helpers()


class AuthClient:
    def __init__(
        self, client: AsyncClient, user: dict[str, str], db: AsyncSession
    ) -> None:
        self.client = client
        self.db = db
        self.user = user

    def auth_headers(self, expired: bool = False) -> dict[str, str]:
        token = self.user["access_token"]
        if expired:
            token = "expired_token"
        return {"Authorization": f"Bearer {token}"}

    async def request(self, method: str, url: str, **kwargs: Any) -> Response:
        headers: dict[str, str] = kwargs.pop("headers", {})
        headers.update(self.auth_headers())
        response = await self.client.request(method, url, headers=headers, **kwargs)
        return response

    async def get(self, url: str, **kwargs: Any) -> Response:
        response = await self.request(method="GET", url=url, **kwargs)
        return response

    async def post(self, url: str, **kwargs: Any) -> Response:
        response = await self.request(method="POST", url=url, **kwargs)
        return response

    async def put(self, url: str, **kwargs: Any) -> Response:
        response = await self.request(method="PUT", url=url, **kwargs)
        return response

    async def delete(self, url: str, **kwargs: Any) -> Response:
        response = await self.request(method="DELETE", url=url, **kwargs)
        return response

    async def noauth_get(self, url: str, **kwargs: Any) -> Response:
        response = await self.client.get(url=url, **kwargs)
        return response

    async def noauth_post(self, url: str, **kwargs: Any) -> Response:
        response = await self.client.post(url=url, **kwargs)
        return response

    async def noauth_put(self, url: str, **kwargs: Any) -> Response:
        response = await self.client.put(url=url, **kwargs)
        return response

    async def noauth_delete(self, url: str, **kwargs: Any) -> Response:
        response = await self.client.delete(url=url, **kwargs)
        return response


@pytest_asyncio.fixture
async def auth_client(
    client: AsyncClient, db: AsyncSession, helpers: Helpers
) -> AuthClient:
    user: dict[str, str] = await helpers.full_login(client)

    return AuthClient(client, user, db=db)
