from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast

from pydantic import BaseModel

from src.infra.application.exception import AppError


T = TypeVar("T", bound=BaseModel)
E = TypeVar("E", bound=AppError)


@dataclass(frozen=True, slots=True, match_args=True)
class Result(Generic[T, E]):
    value: T | None
    error: E | None

    def __post_init__(self):
        if self.value is None and self.error is None:
            raise ValueError("value or error is required")

        if self.value is not None and self.error is not None:
            raise ValueError("cannot use both value and error")

    @classmethod
    def ok(cls, value: T) -> "Result[T, Any]":
        return cls(value=value, error=None)

    @classmethod
    def fail(cls, error: E) -> "Result[Any, E]":
        return cls(value=None, error=error)

    def unwrap(self) -> T:
        """
        Returns the success value or raise error on fail.
        """
        if self.error:
            raise self.error
        return cast(T, self.value)
