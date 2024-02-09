import logging
import uuid

from fastapi import Depends

from src.infra.application.exception import NotFoundError
from src.infra.application.result import Result
from src.infra.database.session import AsyncSession
from src.service.user.dto import UserOut
from src.service.user.repository import UserRepository


logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo

    async def get_user_by_id(
        self,
        *,
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> Result[UserOut, NotFoundError]:
        logger.info("get user by user_id %s", user_id)
        either_user_or_err = await self.user_repo.get_user_by_id(
            session=session,
            user_id=user_id,
        )

        match either_user_or_err:
            case Result(user_found, None):
                return Result.ok(
                    UserOut.model_validate(user_found),
                )

        logger.info("user not found: user_id=%s", user_id)
        return Result.fail(
            NotFoundError(f"user not found: user_id={user_id}"),
        )
