import alembic.command
import alembic.config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import AppConfig
from src.infra.application.factory import app_factory
from src.infra.database.session import async_session_factory, get_session
from tests.base import get_test_app_config, get_test_alembic_config


@pytest.fixture(scope="session")
def test_app_config() -> AppConfig:
    return get_test_app_config()


@pytest.fixture(scope="session")
def test_alembic_config(test_app_config: AppConfig) -> alembic.config.Config:
    return get_test_alembic_config(test_app_config)


@pytest.fixture(autouse=True)
def auto_prune_database(test_alembic_config: alembic.config.Config):
    alembic.command.upgrade(test_alembic_config, revision="head")
    yield
    alembic.command.downgrade(test_alembic_config, revision="base")


@pytest.mark.asyncio
@pytest.fixture(scope="session")
async def test_app(test_app_config):
    return app_factory(test_app_config)


@pytest.fixture
async def test_session(test_app_config: AppConfig):
    test_engine = create_async_engine(str(test_app_config.pg_dsn))
    async_session_factory.configure(bind=test_engine)

    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
def client(test_app, test_session):
    async def get_test_session():
        yield test_session

    test_app.dependency_overrides[get_session] = get_test_session

    yield TestClient(test_app)
