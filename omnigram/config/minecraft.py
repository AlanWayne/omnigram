from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class MinecraftSettings(BaseSettings):
    path: str = ""
    target: str = ""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="MC_",
        env_file=".env",
        extra="ignore",
    )
