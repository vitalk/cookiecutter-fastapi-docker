from uuid import UUID

from pydantic import BaseModel, EmailStr


class AuthIn(BaseModel):
    email: EmailStr
    password: str


class JWTPayload(BaseModel):
    user_id: UUID


class AuthOut(JWTPayload):
    access_token: str
