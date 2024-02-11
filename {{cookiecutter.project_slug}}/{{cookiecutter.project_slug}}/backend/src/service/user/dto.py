import uuid

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class OrmBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserInDto(BaseModel):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: EmailStr
    password: str


class UserOutDto(OrmBase):
    user_id: uuid.UUID
    email: EmailStr
