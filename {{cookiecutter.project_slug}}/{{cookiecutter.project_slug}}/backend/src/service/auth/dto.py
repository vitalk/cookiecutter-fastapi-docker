from uuid import UUID

from pydantic import BaseModel, EmailStr


class AccessTokenInDto(BaseModel):
    email: EmailStr
    password: str


class JWTPayloadDto(BaseModel):
    user_id: UUID


class AccessTokenOutDto(BaseModel):
    access_token: str
    user_id: UUID
