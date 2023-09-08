from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: PostgresDsn | str
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int = 1 * 24 * 60  # one day


settings = Settings()
