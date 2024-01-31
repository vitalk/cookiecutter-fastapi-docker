import asyncio

from starlette.types import ASGIApp
import uvicorn

from src.config import AppConfig, get_config
from src.infra.application.factory import app_factory
from src.infra.application.pre_flight_check import pre_flight_check


def create_app() -> ASGIApp:
    config = get_config()
    app = app_factory(config)
    return app


async def run_app() -> None:
    await pre_flight_check()

    config: AppConfig = get_config()

    uvicorn.run(
        f"{__name__}:create_app",
        host=str(config.app_host.host),
        port=int(config.app_host.port),  # type: ignore[arg-type]
        reload=config.environment.is_debug,
        factory=True,
    )


if __name__ == "__main__":
    asyncio.run(run_app())
