from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas import player_schemas
from services import player_service

router = APIRouter(prefix="/players", tags=["Players"])


@router.get(
    path="/{team_id}",
    status_code=status.HTTP_200_OK,
    response_model=player_schemas.Alt_Team_Players,
)
async def get_team_players(db: AsyncSession = Depends(get_db)):
    team_players = await player_service.get_player_choices(db)

    return team_players
