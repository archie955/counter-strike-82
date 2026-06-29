from pydantic import BaseModel, ConfigDict

from models.enums import Majors, Nationality, Roles

config = ConfigDict(from_attributes=True)


class Player(BaseModel):
    id: int
    team_id: int
    name: str
    nationality: Nationality
    major: Majors
    role: list[Roles]
    hltv: float
    igl: int | None
    model_config = config


class Team_Players(BaseModel):
    players: list[Player]
    model_config = config


class Alt_Team_Players(Team_Players):
    team_id: int
    model_config = config
