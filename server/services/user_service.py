import logging

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.auth import create_access_token
from exceptions.app_exceptions import (
    BadRequestError,
    DataAlreadyExistsError,
    InvalidCredentialsError,
)
from models import models
from schemas import token_schemas, user_schemas
from services.helpers import safe_commit
from utils import utils

logger = logging.getLogger(__name__)


async def create_user(
    db: AsyncSession, user: user_schemas.UserCreate
) -> user_schemas.UserOut:
    existing_user = (
        await db.execute(
            select(models.User).where(
                or_(
                    models.User.email == user.email,
                    models.User.username == user.username,
                )
            )
        )
    ).scalar_one_or_none()

    if existing_user:
        raise DataAlreadyExistsError(datatype="User")

    new_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=utils.hash(user.password),
    )

    db.add(new_user)

    await safe_commit(db=db, datatype="User")
    await db.refresh(new_user)

    logger.info("User created", extra={"user_id": new_user.id})

    return user_schemas.UserOut.model_validate(new_user)


async def login(
    db: AsyncSession, username: str, password: str
) -> token_schemas.UserToken:
    user = (
        await db.execute(
            select(models.User).where(
                or_(
                    models.User.email == username,
                    models.User.username == username,
                )
            )
        )
    ).scalar_one_or_none()

    if not (user and utils.verify(password, user.hashed_password)):
        raise InvalidCredentialsError()

    user_data = {"sub": str(user.id)}

    logger.info("User logged in", extra={"user_id": user.id})

    return token_schemas.UserToken(
        user=user_schemas.UserOut.model_validate(user),
        access_token=create_access_token(data=user_data),
        token_type="bearer",
    )


async def update(
    db: AsyncSession, user: models.User, updated: user_schemas.UserUpdate
) -> user_schemas.UserOut:
    if not utils.verify(updated.password, user.hashed_password):
        raise InvalidCredentialsError()

    updated_user = updated.updated_user

    if (
        user.email == updated_user.email
        and utils.verify(updated_user.password, user.hashed_password)
        and user.username == updated_user.username
    ):
        raise BadRequestError(message="No new information provided, nothing updated")

    user.email = updated_user.email
    user.username = updated_user.username
    user.hashed_password = utils.hash(updated_user.password)

    await db.commit()
    await db.refresh(user)

    logger.info("User updated", extra={"user_id": user.id})

    return user_schemas.UserOut.model_validate(user)


async def delete(db: AsyncSession, user: models.User):
    await db.delete(user)
    await db.commit()

    logger.info("User deleted", extra={"user_id": user.id})

    return
