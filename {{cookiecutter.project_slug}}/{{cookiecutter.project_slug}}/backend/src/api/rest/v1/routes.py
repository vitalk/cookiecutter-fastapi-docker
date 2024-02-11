from fastapi import APIRouter

from src.api.rest.v1.auth.routes import auth_router
from src.api.rest.v1.user.routes import user_router


api_v1_router = APIRouter()

api_v1_router.include_router(
    auth_router, tags=["Auth"], prefix="/auth"
)
api_v1_router.include_router(
    user_router, tags=["User"], prefix="/users"
)
