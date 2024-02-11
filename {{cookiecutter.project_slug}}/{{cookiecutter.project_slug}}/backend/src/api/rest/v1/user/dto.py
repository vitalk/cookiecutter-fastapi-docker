import uuid

from pydantic import BaseModel, EmailStr, Field


class CreateUserDto(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserDto(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
