import uuid

from src.infra.application.exception import BadRequestError, NotFoundError
from src.infra.application.result import Result
from src.infra.database.models import User
from src.infra.database.repository import GenericRepository
from src.infra.database.session import AsyncSession


class UserRepository(GenericRepository[User]):
    orm_model = User

    async def get_user_by_id(
        self,
        *,
        session: AsyncSession,
        user_id: uuid.UUID,
        with_for_update: bool = False,
    ) -> Result[User, NotFoundError]:
        return await self.get_record(
            session=session,
            user_id=user_id,
            with_for_update=with_for_update,
        )

    async def get_user_by_email(
        self,
        *,
        session: AsyncSession,
        email: str,
        with_for_update: bool = False,
    ) -> Result[User, NotFoundError]:
        return await self.get_record(
            session=session,
            email=email,
            with_for_update=with_for_update,
        )

    async def create_user(
        self,
        *,
        session: AsyncSession,
        user_id: uuid.UUID,
        email: str,
        password: bytes,
    ) -> Result[User, BadRequestError]:
        return await self.create_record(
            session=session,
            user_id=user_id,
            email=email,
            password=password,
        )
