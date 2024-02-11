import abc
from typing import Any, Generic, Type, final

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.application.exception import BadRequestError, NotFoundError
from src.infra.application.result import Result
from src.infra.database.declarative_base import OrmModel


class GenericRepository(abc.ABC, Generic[OrmModel]):
    """
    Implements generic interface to access database.
    """

    @abc.abstractproperty
    def orm_model(self) -> Type[OrmModel]:
        ...

    @final
    async def get_record(
        self,
        *,
        session: AsyncSession,
        with_for_update: bool = False,
        **props: Any,
    ) -> Result[OrmModel, NotFoundError]:
        orm_model = self.orm_model
        select_query = select(orm_model)

        or_criteria = [
            (getattr(orm_model, prop_name) == prop_value)
            for prop_name, prop_value in props.items()
        ]
        if or_criteria:
            select_query = select_query.where(*or_criteria)

        if with_for_update:
            select_query = select_query.with_for_update()

        query_result = await session.execute(select_query)
        record_found = query_result.scalars().first()

        if not record_found:
            return Result.fail(NotFoundError())

        return Result.ok(record_found)

    @final
    async def create_record(
        self,
        *,
        session: AsyncSession,
        **props: Any,
    ) -> Result[OrmModel, BadRequestError]:
        orm_model = self.orm_model

        insert_query = (
            insert(orm_model)
            .values(
                **props,
            )
            .returning(orm_model)
        )

        try:
            query_result = await session.execute(insert_query)
        except IntegrityError as err:
            return Result.fail(
                BadRequestError(str(err)),
            )

        return Result.ok(
            query_result.scalars().one(),
        )
