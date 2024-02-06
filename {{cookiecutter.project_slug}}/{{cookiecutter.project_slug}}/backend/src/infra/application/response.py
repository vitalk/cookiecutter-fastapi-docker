from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class Response(BaseModel, Generic[T]):
    result: T


class ListResponse(BaseModel, Generic[T]):
    result: list[T]
