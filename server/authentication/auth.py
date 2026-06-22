from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from exceptions.app_exceptions import InvalidCredentialsError
from models import user_models
from schemas import token_schemas
from utils.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
CREDENTIALS_EXCEPTION = InvalidCredentialsError(headers={"WWW-Authenticate": "Bearer"})


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.exceptions.InvalidTokenError:
        raise CREDENTIALS_EXCEPTION


def verify_access_token(token: str) -> token_schemas.TokenData:
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise CREDENTIALS_EXCEPTION

    user_id = payload.get("sub")

    if user_id is None:
        raise CREDENTIALS_EXCEPTION

    return token_schemas.TokenData(id=user_id)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> user_models.User:
    user_id_token = verify_access_token(token=token)

    user = (
        await db.execute(
            select(user_models.User).where(user_models.User.id == int(user_id_token.id))
        )
    ).scalar_one_or_none()

    if not user:
        raise CREDENTIALS_EXCEPTION

    return user
