from pydantic import BaseModel

from schemas.user_schemas import UserOut


class UserToken(BaseModel):
    user: UserOut
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str
