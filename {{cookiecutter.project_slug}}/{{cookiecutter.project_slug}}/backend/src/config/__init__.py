from functools import lru_cache
from typing import Final

from dotenv import find_dotenv, load_dotenv

from src.config.config import AppConfig


load_dotenv(find_dotenv())


@lru_cache
def get_config() -> AppConfig:
    return AppConfig()  # type: ignore[call-arg]


config: Final[AppConfig] = get_config()
