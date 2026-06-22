from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

config = ConfigDict(from_attributes=True)


class User(BaseModel):
    email: EmailStr
    username: str


class UserCreate(User):
    password: str


class UserOut(User):
    model_config = config
    id: int
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    updated_user: UserCreate
    password: str
