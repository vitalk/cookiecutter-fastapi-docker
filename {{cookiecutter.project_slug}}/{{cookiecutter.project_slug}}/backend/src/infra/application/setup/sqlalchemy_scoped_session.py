from typing import Awaitable, Callable
import uuid

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.infra.database.session import (
    reset_scoped_session,
    scoped_session,
    set_scoped_session,
)


class ScopedSessionMiddleware:
    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        session_id = uuid.uuid4().hex
        reset_token = set_scoped_session(session_id=session_id)
        try:
            return await call_next(request)
        finally:
            await scoped_session.remove()
            reset_scoped_session(token=reset_token)


def setup_sqlalchemy_scoped_session(app: FastAPI) -> None:
    app.add_middleware(
        BaseHTTPMiddleware,
        dispatch=ScopedSessionMiddleware(),
    )
