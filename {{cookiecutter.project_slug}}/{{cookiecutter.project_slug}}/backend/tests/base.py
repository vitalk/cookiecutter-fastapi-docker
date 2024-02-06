import os

import alembic.config

from src.config import AppConfig


def get_test_app_config() -> AppConfig:
    return AppConfig(  # type: ignore[call-arg]
        pg_dsn=os.getenv("TEST_PG_DSN"),  # type: ignore[arg-type]
    )


def get_test_alembic_config(test_app_config: AppConfig) -> alembic.config.Config:
    alembic_config = alembic.config.Config("alembic.ini")
    alembic_config.set_main_option(
        "sqlalchemy.url",
        str(test_app_config.pg_dsn),
    )

    return alembic_config


class BaseTestCase:
    base_url: str

    def get_url(self) -> str:
        return self.base_url
