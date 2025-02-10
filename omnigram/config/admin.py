from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class AdminSettings(BaseSettings):
    sudo: int

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="ADM_",
        env_file=".env",
        extra="ignore",
    )
