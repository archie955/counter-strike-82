from pydantic import BaseModel, ConfigDict

from models.enums import Majors, Nationality, Roles

config = ConfigDict(from_attributes=True)


class Player(BaseModel):
    id: int
    name: str
    team_id: int
    nationality: Nationality
    major: Majors
    role: Roles
    hltv: float
    igl: int | None
    model_config = config


class Team_Players(BaseModel):
    players: list[Player]
    model_config = config
