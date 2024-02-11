from datetime import datetime, timedelta
import logging
from typing import cast

import bcrypt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
from src.infra.application.exception import NotFoundError
from src.infra.application.result import Result
from src.infra.database.models import User
from src.service.auth.dto import (
    AccessTokenInDto,
    AccessTokenOutDto,
    JWTPayloadDto,
)
from src.service.auth.exception import (
    InvalidCredentialError,
    InvalidTokenError,
)
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
    ) -> Result[JWTPayloadDto, InvalidTokenError]:
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
            JWTPayloadDto(
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
        access_token_in: AccessTokenInDto,
    ) -> Result[AccessTokenOutDto, InvalidCredentialError]:
        logger.info(
            "trying to authenticate user by email: email=%s",
            access_token_in.email,
        )
        user_or_err = await self.user_repo.get_user_by_email(
            session=session,
            email=access_token_in.email,
        )
        match user_or_err:
            case Result(None, NotFoundError()):
                logger.info("given user not found: email=%s", access_token_in.email)
                return Result.fail(InvalidCredentialError())

        user_found = cast(User, user_or_err.value)
        logger.info("user found: user_id=%s", user_found.user_id)

        if not self.check_password(
            password=access_token_in.password,
            hashed_password=user_found.password,
        ):
            logger.info(
                "password missmatch for user: user_id=%s given password=%s",
                user_found.user_id,
                access_token_in.password,
            )
            return Result.fail(InvalidCredentialError())

        access_token = self.create_access_token(user=user_found)

        return Result.ok(
            AccessTokenOutDto(
                user_id=user_found.user_id,
                access_token=access_token,
            )
        )

    def check_password(
        self,
        *,
        password: str,
        hashed_password: bytes,
    ) -> bool:
        password_bytes = bytes(password, "utf-8")
        return bcrypt.checkpw(password_bytes, hashed_password)

    def hash_password(
        self,
        *,
        password: str,
    ) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)
