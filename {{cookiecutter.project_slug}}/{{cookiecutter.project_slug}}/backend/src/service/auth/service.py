from datetime import datetime, timedelta
import logging
from typing import cast

import bcrypt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt

from src.config import config
from src.infra.application.exception import NotFoundError
from src.infra.application.result import Result
from src.infra.database.models import User
from src.infra.database.session import AsyncSession
from src.service.auth.dto import AuthIn, AuthOut, JWTPayload
from src.service.auth.exception import (
    EmailTakenError,
    InvalidCredentialError,
    InvalidTokenError,
)
from src.service.user.dto import UserIn, UserOut
from src.service.user.repository import UserRepository


logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer("/api/1/auth/token")


class AuthService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo

    @staticmethod
    async def check_jwt_token(
        *,
        token: str = Depends(oauth2_scheme),
    ) -> Result[JWTPayload, InvalidTokenError]:
        if not token:
            logger.debug("no jwt token is given, abort mission")
            return Result.fail(InvalidTokenError())

        try:
            jwt_payload = jwt.decode(
                token,
                key=config.jwt_secret,
                algorithms=[
                    config.jwt_algorithm,
                ],
            )

        except jwt.PyJWTError as err:
            logger.error("invalid jwt token is given: %s", str(err))
            return Result.fail(InvalidTokenError(str(err)))

        return Result.ok(
            JWTPayload(
                user_id=jwt_payload["sub"],
            )
        )

    def create_access_token(self, *, user: User) -> str:
        expires_in = timedelta(minutes=config.jwt_exp)

        jwt_payload = {
            "sub": str(user.user_id),
            "exp": datetime.utcnow() + expires_in,
        }

        return jwt.encode(
            jwt_payload,
            key=config.jwt_secret,
            algorithm=config.jwt_algorithm,
        )

    async def authenticate_user(
        self,
        *,
        session: AsyncSession,
        auth_in: AuthIn,
    ) -> Result[AuthOut, InvalidCredentialError]:
        logger.info(
            "trying to authenticate user by email: email=%s",
            auth_in.email,
        )
        maybe_user = await self.user_repo.get_user_by_email(
            session=session,
            email=auth_in.email,
        )
        match maybe_user:
            case Result(None, NotFoundError()):
                logger.info("given user not found: email=%s", auth_in.email)
                return Result.fail(InvalidCredentialError())

        user_found = cast(User, maybe_user.value)
        logger.info("user found: user_id=%s", user_found.user_id)

        if not self.check_password(
            password=auth_in.password,
            password_in_db=user_found.password,
        ):
            logger.info(
                "password missmatch for user: user_id=%s given password=%s",
                user_found.user_id,
                auth_in.password,
            )
            return Result.fail(InvalidCredentialError())

        access_token = self.create_access_token(user=user_found)

        return Result.ok(
            AuthOut(
                user_id=user_found.user_id,
                access_token=access_token,
            )
        )

    def check_password(
        self,
        *,
        password: str,
        password_in_db: bytes,
    ) -> bool:
        password_bytes = bytes(password, "utf-8")
        return bcrypt.checkpw(password_bytes, password_in_db)

    def hash_password(
        self,
        *,
        password: str,
    ) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    async def create_user(
        self,
        *,
        session: AsyncSession,
        auth_in: AuthIn,
    ) -> Result[UserOut, EmailTakenError]:
        logger.info("check user email is not taken: email=%s", auth_in.email)
        maybe_user = await self.user_repo.get_user_by_email(
            session=session,
            email=auth_in.email,
            with_for_update=True,
        )

        match maybe_user:
            case Result(user_record, None):  # noqa: F841
                logger.info(
                    "unable to create a new user: the given email %s is already taken",
                    auth_in.email,
                )
                return Result.fail(
                    EmailTakenError(
                        "unable to create a new user: the given email is already taken"
                    )
                )

        hashed_password = self.hash_password(password=auth_in.password)

        logger.info("create a new user: email=%s", auth_in.email)
        maybe_new_user = await self.user_repo.create_user(
            session=session,
            user_in=UserIn(
                email=auth_in.email,
                password=hashed_password,
            ),
        )

        match maybe_new_user:
            case Result(new_user, None):
                new_user = cast(User, new_user)
                logger.info(
                    "new user created with user_id %s",
                    new_user.user_id,
                )
                return Result.ok(
                    UserOut.model_validate(new_user),
                )

            case _:
                logger.info(
                    "unable to create a new user: %s",
                    str(maybe_new_user.error),
                )
                return Result.fail(
                    EmailTakenError(
                        "unable to create a new user: the given email is already taken"
                    )
                )
