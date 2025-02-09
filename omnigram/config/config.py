from pydantic_settings import BaseSettings
from .telegram import TelegramSettings


class Config(BaseSettings):
    telegram: TelegramSettings = TelegramSettings()
