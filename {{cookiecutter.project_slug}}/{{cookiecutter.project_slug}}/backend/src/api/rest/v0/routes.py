from fastapi import APIRouter

from src.api.rest.v0.health_check.routes import health_check_router


api_v0_router = APIRouter()

api_v0_router.include_router(
    health_check_router, tags=["Telemetry"], prefix="/health"
)
