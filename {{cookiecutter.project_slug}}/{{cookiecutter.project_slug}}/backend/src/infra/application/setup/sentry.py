import logging

from fastapi import FastAPI
import sentry_sdk

from src.config import AppConfig


logger = logging.getLogger(__name__)


def setup_sentry(app: FastAPI, config: AppConfig) -> None:
    if config.sentry_dsn:
        logger.info(
            "use sentry_dsn [%s]",
            config.sentry_dsn.with_password("***"),
        )
        sentry_sdk.init(
            str(config.sentry_dsn),
            traces_sample_rate=1.0,
        )

        if config.environment.is_debug and config.sentry_debug_path:
            logger.info(
                "sentry debug handler attached to path [%s]",
                config.sentry_debug_path,
            )

            @app.get(config.sentry_debug_path, tags=["Telemetry"])
            async def trigger_error():
                division_by_zero = 1 / 0  # noqa: F841

        else:
            logger.info("no sentry_debug_path specified, skipped")

    else:
        logger.info("no sentry_dsn specified, skipped")
