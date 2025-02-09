from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramSettings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="TG_",
        env_file=".env",
        extra="ignore",
    )
