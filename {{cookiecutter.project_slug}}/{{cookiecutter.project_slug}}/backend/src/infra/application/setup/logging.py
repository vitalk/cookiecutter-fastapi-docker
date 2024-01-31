import asyncio
import atexit
from contextlib import suppress
from dataclasses import dataclass, field
import logging
import logging.handlers
import sys
import threading
import time
from types import MappingProxyType
from typing import Any, Callable, Final

from src.config import AppConfig
from src.infra.application.setup.tracing import get_trace_id


F = Callable[..., Any]


def setup_logging(config: AppConfig) -> None:
    log_level = logging.getLevelName(config.log_level.upper())
    log_format = config.log_format

    stream_handler = _create_logging_handler(log_format)
    buffered_handler = _wrap_logging_handler(
        stream_handler,
        loop=asyncio.get_running_loop(),
        buffer_size=config.log_buffer_size,
        flush_interval=config.log_flush_interval,
    )

    logging.basicConfig(
        format=log_format,
        level=log_level,
        handlers=[
            buffered_handler,
        ],
    )


_trace_id_record_attr: Final[str] = "trace_id"
_trace_id_record_default_value: Final[str] = "-"


@dataclass
class TraceIdFilter(logging.Filter):
    name: str = field(default=_trace_id_record_attr)
    default_value: str = field(default=_trace_id_record_default_value)

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Used to attach Trace ID value to the log record via ``name``
        attribute.
        """
        setattr(record, self.name, get_trace_id(self.default_value))
        return True


class BufferedHandler(logging.handlers.MemoryHandler):
    """
    Used to resolve value of trace_id contextvar on emit. Otherwise the log
    record may contains stale value of the contextvar.
    """

    def emit(self, record: logging.LogRecord) -> None:
        setattr(record, _trace_id_record_attr, get_trace_id())
        return super().emit(record)


def _safe_flush_handler(
    handler: logging.handlers.MemoryHandler,
) -> None:
    with suppress(Exception):
        if handler.buffer:
            handler.flush()


def _create_logging_handler(
    log_format: str,
) -> logging.Handler:
    handler = logging.StreamHandler(stream=sys.stdout)

    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    return handler


def _wrap_logging_handler(
    handler: logging.Handler,
    *,
    loop: asyncio.AbstractEventLoop,
    buffer_size: int,
    flush_interval: float | int,
) -> logging.Handler:
    buffered_handler = BufferedHandler(
        buffer_size,
        target=handler,
        flushLevel=logging.CRITICAL,
    )

    _run_in_thread(
        _threaded_flush_handler,
        args=(
            buffered_handler,
            flush_interval,
            loop,
        ),
        deattach=True,
    )

    atexit.register(
        _safe_flush_handler,
        buffered_handler,
    )

    return buffered_handler


def _threaded_flush_handler(
    handler: logging.handlers.MemoryHandler,
    flush_interval: int | float,
    loop: asyncio.AbstractEventLoop,
) -> None:
    def has_target() -> bool:
        return bool(handler.target)

    def has_no_target() -> bool:
        return False

    is_target = has_no_target
    if isinstance(handler, logging.handlers.MemoryHandler):
        is_target = has_target

    while not loop.is_closed() and is_target():
        _safe_flush_handler(handler)
        time.sleep(flush_interval)


def _run_in_thread(
    fun: F,
    *,
    args: Any = (),
    kwargs: Any = MappingProxyType({}),
    deattach: bool = True,
) -> threading.Thread:
    thread = threading.Thread(
        target=fun,
        name=fun.__name__,
        args=args,
        kwargs=kwargs,
        daemon=deattach,
    )
    thread.start()
    return thread
