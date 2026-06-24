from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas import team_schemas
from services import team_service

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get(path="", status_code=status.HTTP_200_OK, response_model=team_schemas.Teams)
async def get_teams(db: AsyncSession = Depends(get_db)):
    teams = await team_service.get(db)

    return teams
