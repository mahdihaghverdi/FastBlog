from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: PostgresDsn | str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1 * 24 * 60  # one day
    access_token_url: str = "access-token"


settings = Settings()
