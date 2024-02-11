import logging

from fastapi import FastAPI
from starlette.types import ASGIApp

from src.api.rest.v0.routes import api_v0_router
from src.api.rest.v1.routes import api_v1_router
from src.config import AppConfig
from src.infra.application.setup.cors import setup_cors_middleware
from src.infra.application.setup.logging import setup_logging
from src.infra.application.setup.sentry import setup_sentry
from src.infra.application.setup.sqlalchemy_scoped_session import (
    setup_sqlalchemy_scoped_session,
)
from src.infra.application.setup.tracing import setup_tracing_middleware


logger = logging.getLogger(__name__)


def app_factory(config: AppConfig) -> ASGIApp:
    setup_logging(config)

    logger.info("starting app")

    app_props = {
        "title": config.app_name,
        "docs_url": config.docs_url,
        "openapi_url": config.openapi_url,
        "redoc_url": None,
    }

    if config.environment.is_deployed:
        app_props["docs_url"] = None
        app_props["redoc_url"] = None
        app_props["openapi_url"] = None
        logger.info(
            "swagger documentation was hidden due to security reasons",
        )
    else:
        logger.info(
            "swagger documentation available at %s and %s",
            config.docs_url,
            config.openapi_url,
        )

    app = FastAPI(**app_props)  # type: ignore[arg-type]

    logger.info("setup sentry")
    setup_sentry(app, config)

    if config.environment.is_debug:
        logger.info("app started with config")
        masked_config = config.get_config_copy_with_masked_passwords()
        for prop, value in dict(masked_config).items():
            logger.info(" config [%s] has value [%s]", prop, value)

    logger.info("setup middlewares")

    setup_cors_middleware(app, config)
    setup_tracing_middleware(app, config)
    setup_sqlalchemy_scoped_session(app)

    app.include_router(
        api_v0_router,
        prefix="/api/0",
    )

    app.include_router(
        api_v1_router,
        prefix="/api/1",
    )

    logger.info("app is ready")

    return app
