from functools import lru_cache
from typing import Final

from src.config.config import AppConfig


@lru_cache
def get_config() -> AppConfig:
    return AppConfig()  # type: ignore[call-arg]


config: Final[AppConfig] = get_config()
