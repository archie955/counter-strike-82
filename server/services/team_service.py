import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import models
from schemas import team_schemas

logger = logging.getLogger(__name__)


async def get(db: AsyncSession) -> team_schemas.Teams:
    teams = (
        (
            await db.execute(
                select(models.Team).options(selectinload(models.Team.players))
            )
        )
        .scalars()
        .all()
    )

    team_list = [team_schemas.Team.model_validate(t) for t in teams]

    return team_schemas.Teams(teams=team_list)
