from pydantic import BaseModel, ConfigDict

config = ConfigDict(from_attributes=True)


class Team(BaseModel):
    id: int
    name: str
    igl: bool
    awp: bool


class Teams(BaseModel):
    teams: list[Team]
