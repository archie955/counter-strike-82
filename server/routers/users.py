from fastapi import APIRouter, Depends, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from authentication import auth
from database.database import get_db
from models import models
from schemas import token_schemas, user_schemas
from services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    path="", status_code=status.HTTP_201_CREATED, response_model=user_schemas.UserOut
)
async def create_user(
    user: user_schemas.UserCreate, db: AsyncSession = Depends(get_db)
):
    new_user = await user_service.create_user(db=db, user=user)

    return new_user


@router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    response_model=token_schemas.UserToken,
)
async def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user_token = await user_service.login(
        db=db, username=user_credentials.username, password=user_credentials.password
    )

    return user_token


@router.put("", status_code=status.HTTP_200_OK, response_model=user_schemas.UserOut)
async def update_user(
    updated_payload: user_schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    updated_user = await user_service.update(db=db, user=user, updated=updated_payload)

    return updated_user


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    await user_service.delete(db=db, user=user)
    return
