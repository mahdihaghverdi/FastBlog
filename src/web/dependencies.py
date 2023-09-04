from functools import lru_cache

from src.web.config import Settings


@lru_cache
def get_settings():
    return Settings()
