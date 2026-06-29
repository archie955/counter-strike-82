import logging
from random import randint

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from exceptions.app_exceptions import DataNotFoundError
from models import models
from schemas import player_schemas

logger = logging.getLogger(__name__)

NUMBER_OF_TEAMS = 100


async def get_team_players(
    team_id: int, db: AsyncSession
) -> player_schemas.Team_Players:
    team = (
        await db.execute(
            select(models.Team)
            .options(selectinload(models.Team.players))
            .where(models.Team.id == team_id)
        )
    ).scalar_one_or_none()

    if not team:
        raise DataNotFoundError(datatype="Team")

    if not team.players:
        raise DataNotFoundError(datatype="Players")

    logger.info(
        "Players fetched",
        extra={"team_id": team_id, "players_fetched": len(team.players)},
    )

    players_list = [player_schemas.Player.model_validate(p) for p in team.players]

    return player_schemas.Team_Players(players=players_list)


async def get_player_choices(db: AsyncSession) -> player_schemas.Alt_Team_Players:
    rand = randint(0, NUMBER_OF_TEAMS - 1)
    team = (
        await db.execute(
            select(models.Team)
            .options(selectinload(models.Team.players))
            .where(models.Team.id == rand)
        )
    ).scalar_one_or_none()

    if not team:
        raise DataNotFoundError(datatype="Team")

    if not team.players:
        raise DataNotFoundError(datatype="Players")

    logger.info(
        "Players fetched",
        extra={"team_id": rand, "players_fetched": len(team.players)},
    )

    players_list = [player_schemas.Player.model_validate(p) for p in team.players]

    return player_schemas.Alt_Team_Players(team_id=rand, players=players_list)
