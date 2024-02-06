import logging

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.infra.application.response import Response
from src.infra.database.session import AsyncSession, get_session
from src.service.auth.dependency import check_jwt_token
from src.service.auth.dto import AuthIn, AuthOut, JWTPayload
from src.service.auth.service import AuthService
from src.service.user.dto import UserOut
from src.service.user.service import UserService


auth_router = APIRouter()


logger = logging.getLogger(__name__)


@auth_router.post(
    "/login",
    response_model=AuthOut,
    summary="Generate a new access_token for user (used by Swagger)",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(),
    session: AsyncSession = Depends(get_session),
) -> AuthOut:
    token_claim = await auth_service.authenticate_user(
        session=session,
        auth_in=AuthIn(
            email=form_data.username,
            password=form_data.password,
        ),
    )

    return token_claim.unwrap()


@auth_router.post(
    "/token",
    response_model=Response[AuthOut],
    summary="Generate new access_token for user",
)
async def get_jwt_token(
    auth_in: AuthIn,
    auth_service: AuthService = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Response[AuthOut]:
    token_claim = await auth_service.authenticate_user(
        session=session,
        auth_in=auth_in,
    )

    return Response(result=token_claim.unwrap())


@auth_router.post(
    "/users",
    response_model=Response[UserOut],
    summary="Create a new user",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    auth_in: AuthIn,
    auth_service: AuthService = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Response[UserOut]:
    new_user = await auth_service.create_user(
        session=session,
        auth_in=auth_in,
    )

    return Response(result=new_user.unwrap())


@auth_router.get(
    "/users/me",
    response_model=Response[UserOut],
    summary="Get information about authenticated user",
)
async def get_user_me(
    jwt_payload: JWTPayload = Depends(check_jwt_token),
    user_service: UserService = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Response[UserOut]:
    user_found = await user_service.get_user_by_id(
        session=session,
        user_id=jwt_payload.user_id,
    )
    return Response(result=user_found.unwrap())
