"""
Module performs pre-flight check application dependencies.
"""
import asyncio
import logging
from typing import Final

from sqlalchemy import text
from tenacity import (
    after_log,
    before_log,
    retry,
    stop_after_attempt,
    wait_fixed,
)

from src.infra.database.session import async_session_factory


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

max_tries: Final[int] = 60 * 5
wait_seconds: Final[int] = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
)
async def wait_for_deps() -> None:
    try:
        async with async_session_factory() as session:
            await session.execute(text("select true"))
    except Exception as exc:
        logger.error(exc)
        raise exc


async def pre_flight_check() -> None:
    logger.info("service pre-flight check")
    await wait_for_deps()
    logger.info("service pre-flight check finished")


if __name__ == "__main__":
    asyncio.run(pre_flight_check())
