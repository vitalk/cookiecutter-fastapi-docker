import logging
from typing import cast
import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.application.result import Result
from src.infra.database.models import User
from src.infra.database.transactional import transactional
from src.service.auth.service import AuthService
from src.service.user.dto import UserInDto, UserOutDto
from src.service.user.exception import EmailTakenError, UserNotFoundError
from src.service.user.repository import UserRepository


logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        user_repo: UserRepository = Depends(),
        auth_service: AuthService = Depends(),
    ):
        self.user_repo = user_repo
        self.auth_service = auth_service

    @transactional()
    async def create_user(
        self,
        *,
        session: AsyncSession,
        user_in: UserInDto,
    ) -> Result[UserOutDto, EmailTakenError]:
        logger.info("check user email is not taken: email=%s", user_in.email)
        user_or_err = await self.user_repo.get_user_by_email(
            session=session,
            email=user_in.email,
            with_for_update=True,
        )

        match user_or_err:
            case Result(user_record, None):  # noqa: F841
                logger.info(
                    "unable to create a new user: the given email %s is already taken",
                    user_in.email,
                )
                return Result.fail(
                    EmailTakenError(
                        "unable to create a new user: the given email is already taken"
                    )
                )

        hashed_password = self.auth_service.hash_password(
            password=user_in.password,
        )

        logger.info("create a new user: email=%s", user_in.email)
        new_user_or_err = await self.user_repo.create_user(
            session=session,
            user_id=user_in.user_id,
            email=user_in.email,
            password=hashed_password,
        )

        match new_user_or_err:
            case Result(new_user, None):
                new_user = cast(User, new_user)
                logger.info(
                    "new user created with user_id %s",
                    new_user.user_id,
                )
                return Result.ok(
                    UserOutDto.model_validate(new_user),
                )

            case _:
                logger.info(
                    "unable to create a new user: %s",
                    str(new_user_or_err.error),
                )
                return Result.fail(
                    EmailTakenError(
                        "unable to create a new user: the given email is already taken"
                    )
                )

    async def get_user_by_id(
        self,
        *,
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> Result[UserOutDto, UserNotFoundError]:
        logger.info("get user by user_id %s", user_id)
        user_or_err = await self.user_repo.get_user_by_id(
            session=session,
            user_id=user_id,
        )

        match user_or_err:
            case Result(user_found, None):
                return Result.ok(
                    UserOutDto.model_validate(user_found),
                )

        logger.info("user not found: user_id=%s", user_id)
        return Result.fail(
            UserNotFoundError(f"user not found: user_id={user_id}"),
        )
