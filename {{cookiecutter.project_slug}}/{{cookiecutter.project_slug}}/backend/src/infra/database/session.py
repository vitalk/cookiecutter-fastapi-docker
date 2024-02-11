from contextvars import ContextVar, Token
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from src.config import config


_scoped_session: ContextVar[str] = ContextVar("_scoped_session")


def get_scoped_session() -> str:
    return _scoped_session.get()


def set_scoped_session(*, session_id: str) -> Token:
    return _scoped_session.set(session_id)


def reset_scoped_session(*, token: Token) -> None:
    _scoped_session.reset(token)


engine = create_async_engine(str(config.pg_dsn), echo=config.debug)
async_session_factory = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
scoped_session = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_scoped_session,
)


async def get_session() -> AsyncGenerator[
    async_scoped_session[AsyncSession],
    Any,
]:
    yield scoped_session
