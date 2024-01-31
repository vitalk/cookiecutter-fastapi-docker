import logging

from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from src.config import AppConfig


logger = logging.getLogger(__name__)


def setup_cors_middleware(app: FastAPI, config: AppConfig) -> None:
    if config.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=True,
            allow_methods=config.cors_methods,
            allow_headers=config.cors_headers,
        )

        logger.info("cors enabled for")
        logger.info(" origins: %s", [str(o) for o in config.cors_origins])
        logger.info(" methods: %s", config.cors_methods)
        logger.info(" headers: %s", config.cors_headers)
