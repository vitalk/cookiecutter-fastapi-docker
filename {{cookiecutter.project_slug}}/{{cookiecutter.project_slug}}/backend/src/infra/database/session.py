from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import config


engine = create_async_engine(str(config.pg_dsn), echo=config.debug)
async_session = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session() as session:
        yield session
