import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.v1.user.dto import CreateUserDto, UserDto
from src.infra.application.response import Response
from src.infra.database.session import get_session
from src.service.auth.dependency import check_jwt_token
from src.service.auth.dto import JWTPayloadDto
from src.service.user.dto import UserInDto
from src.service.user.service import UserService


user_router = APIRouter()


logger = logging.getLogger(__name__)


@user_router.post(
    "/",
    response_model=Response[UserDto],
    summary="Create a new user",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data_in: CreateUserDto,
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_session),
):
    new_user = await user_service.create_user(
        session=session,
        user_in=UserInDto(**data_in.model_dump()),
    )

    return Response(result=new_user.unwrap())


@user_router.get(
    "/me",
    response_model=Response[UserDto],
    summary="Get information about authenticated user",
)
async def get_user_me(
    jwt_payload: JWTPayloadDto = Depends(check_jwt_token),
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user_found = await user_service.get_user_by_id(
        session=session,
        user_id=jwt_payload.user_id,
    )
    return Response(result=user_found.unwrap())
