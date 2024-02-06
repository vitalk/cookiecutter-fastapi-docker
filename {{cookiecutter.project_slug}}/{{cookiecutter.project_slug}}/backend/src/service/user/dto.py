import uuid

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class OrmBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserIn(BaseModel):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: EmailStr
    password: bytes


class UserOut(OrmBase):
    user_id: uuid.UUID
    email: EmailStr
