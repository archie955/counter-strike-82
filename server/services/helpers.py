from enum import Enum

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.app_exceptions import DataAlreadyAddedError, DataAlreadyExistsError


async def safe_commit(db: AsyncSession, datatype: str) -> None:
    try:
        await db.commit()
    except IntegrityError as exc:
        raise DataAlreadyExistsError(datatype) from exc


async def safe_commit_add(db: AsyncSession, datatype: str) -> None:
    try:
        await db.commit()
    except IntegrityError as exc:
        raise DataAlreadyAddedError(datatype) from exc


class Position(str, Enum):
    IGL = "IGL"
    AWP = "AWPer"
    OPEN = "Opener"
    CLOSE = "Closer"
    SUPPORT = "Support"
