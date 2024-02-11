from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.service.auth.dto import JWTPayloadDto
from src.service.auth.service import AuthService


oauth2_scheme = OAuth2PasswordBearer("/api/1/auth/login")


async def check_jwt_token(
    *,
    token: str = Depends(oauth2_scheme),
) -> JWTPayloadDto:
    jwt_payload = await AuthService.check_jwt_token(
        token=token,
    )

    return jwt_payload.unwrap()
