from typing import Any, Callable, TypeVar

from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base


naming_convention: dict[str, str | Callable[..., str]] = {
    "all_column_names": lambda constraint, _: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    "ix": "ix_%(table_name)s_%(all_column_names)s",
    "uq": "uq_%(table_name)s_%(all_column_names)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(all_column_names)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)


class Base(declarative_base(metadata=metadata)):  # type: ignore[misc]
    __abstract__: bool = True

    id: Any
    __name__: str

    @declared_attr  # type: ignore[arg-type]
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()


OrmModel = TypeVar("OrmModel", bound=Base)
