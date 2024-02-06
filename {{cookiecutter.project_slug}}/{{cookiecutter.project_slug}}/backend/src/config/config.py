import logging
import secrets
from typing import Self
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

from src.config.environment import Environment


_AnyLogLevel = Literal["debug", "info", "warning", "error", "critical"]


logger = logging.getLogger(__name__)


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="")

    app_name: str
    app_host: AnyHttpUrl
    app_version: str = "0.0.1"

    environment: Environment = Environment.LOCAL
    debug: bool = environment.is_debug

    openapi_url: str = "/openapi.json"
    docs_url: str = "/docs"

    secret_key: str = secrets.token_urlsafe(32)

    log_buffer_size: int = 1024
    log_flush_interval: int | float = 0.1
    log_format: str = (
        "%(asctime)s %(levelname)s:%(funcName)s:%(lineno)d %(trace_id)s %(message)s"
    )
    log_level: _AnyLogLevel = "debug" if debug else "info"

    trace_header_name: str = "X-Trace-ID"

    pg_dsn: URL | None = None

    @field_validator("pg_dsn", mode="before")
    def coerce_pg_dsn_to_yarl_url(cls, value: str | None) -> URL | None:  # noqa: N805
        return URL(value) if value else None

    cors_origins: list[AnyHttpUrl] = Field(default_factory=list)
    cors_methods: list[str]
    cors_headers: list[str]

    sentry_dsn: URL | None = None
    sentry_debug_path: str | None = None

    @field_validator("sentry_dsn", mode="before")
    def coerce_sentry_dsn_to_yarl_url(cls, value: str) -> URL | None:  # noqa: N805
        return URL(value) if value else None

    def get_config_copy_with_masked_passwords(self) -> Self:
        new_config = {}
        for prop, value in dict(self).items():
            if isinstance(value, URL):
                value = value.with_password("***")

            new_config[prop] = value

        return type(self)(**new_config)

    jwt_exp: int = 5
    jwt_algorithm: str = "HS256"
    jwt_secret: str = secret_key
