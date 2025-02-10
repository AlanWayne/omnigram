from pydantic_settings import BaseSettings

from .admin import AdminSettings
from .minecraft import MinecraftSettings
from .telegram import TelegramSettings


class Config(BaseSettings):
    telegram: TelegramSettings = TelegramSettings()  # type: ignore
    minecraft: MinecraftSettings = MinecraftSettings()  # type: ignore
    admin: AdminSettings = AdminSettings()  # type: ignore
