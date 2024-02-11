import uuid

from pydantic import BaseModel, EmailStr


class CreateAccessTokenDto(BaseModel):
    email: EmailStr
    password: str


class AccessTokenDto(BaseModel):
    user_id: uuid.UUID
    access_token: str
