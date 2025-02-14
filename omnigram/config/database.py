from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    name: str = ""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="DB_",
        env_file=".env",
        extra="ignore",
    )
