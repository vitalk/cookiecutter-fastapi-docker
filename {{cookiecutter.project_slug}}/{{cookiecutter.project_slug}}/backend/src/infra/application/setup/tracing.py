from contextvars import ContextVar
from dataclasses import dataclass, field
import logging
import logging.handlers
from typing import Awaitable, Callable, Final, cast
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware

from src.config import AppConfig


trace_id: ContextVar[str | None] = ContextVar("trace_id", default=None)


logger = logging.getLogger(__name__)

_TRACE_ID_HEADER_NAME: Final = "X-Trace-ID"


def _get_uuid4_hex() -> str:
    return uuid4().hex


def get_trace_id(
    default_value: str = "-",
    max_length: int = 32,
) -> str:
    trace_id_value = cast(str, trace_id.get(default_value))
    return trace_id_value[:max_length] if max_length is not None else trace_id_value


@dataclass
class TracingMiddleware:
    header_name: str = field(default=_TRACE_ID_HEADER_NAME)
    generator: Callable[[], str] = field(default=_get_uuid4_hex)

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Loads Trace Id from incoming headers or generate new one otherwise.
        """
        headers = MutableHeaders(request.headers)

        trace_id_value = self._get_header_value_or_generate_new(
            header_name=self.header_name,
            headers=headers,
        )
        trace_id.set(trace_id_value)

        async def tracing_middleware(
            request: Request,
            call_next: Callable[[Request], Awaitable[Response]],
        ) -> Response:
            response = await call_next(request)
            if trace_id_value := trace_id.get():
                response.headers[self.header_name] = trace_id_value

            return response

        return await tracing_middleware(request, call_next)

    def _get_header_value_or_generate_new(
        self,
        *,
        header_name: str,
        headers: MutableHeaders,
    ) -> str:
        header_value = headers.get(header_name.lower())

        if not header_value:
            return self.generator()

        return header_value


def setup_tracing_middleware(app: FastAPI, config: AppConfig) -> None:
    logger.info(
        "enable tracing using [%s] header",
        config.trace_header_name,
    )

    app.add_middleware(
        BaseHTTPMiddleware,
        dispatch=TracingMiddleware(
            header_name=config.trace_header_name,
        ),
    )
