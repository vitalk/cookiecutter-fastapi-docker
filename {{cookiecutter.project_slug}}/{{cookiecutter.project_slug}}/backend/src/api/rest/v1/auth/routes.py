import logging

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.api.rest.v1.auth.dto import AccessTokenDto, CreateAccessTokenDto
from src.infra.application.response import Response
from src.infra.database.session import AsyncSession, get_session
from src.service.auth.dto import AccessTokenInDto
from src.service.auth.service import AuthService


auth_router = APIRouter()


logger = logging.getLogger(__name__)


@auth_router.post(
    "/login",
    response_model=AccessTokenDto,
    summary="Create a new access token for user",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(),
    session: AsyncSession = Depends(get_session),
):
    token_claim = await auth_service.authenticate_user(
        session=session,
        access_token_in=AccessTokenInDto(
            email=form_data.username,
            password=form_data.password,
        ),
    )

    return token_claim.unwrap()


@auth_router.post(
    "/token",
    response_model=Response[AccessTokenDto],
    summary="Create a new access token for user",
)
async def get_jwt_token(
    data_in: CreateAccessTokenDto,
    auth_service: AuthService = Depends(),
    session: AsyncSession = Depends(get_session),
):
    token_claim = await auth_service.authenticate_user(
        session=session,
        access_token_in=AccessTokenInDto(**data_in.model_dump()),
    )

    return Response(result=token_claim.unwrap())
