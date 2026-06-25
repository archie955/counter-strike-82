from pydantic import BaseModel, ConfigDict

from schemas.player_schemas import Team_Players

config = ConfigDict(from_attributes=True)


class Team(BaseModel):
    id: int
    name: str
    players: Team_Players


class Teams(BaseModel):
    teams: list[Team]
