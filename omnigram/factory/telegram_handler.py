from functools import lru_cache

from omnigram.telegram import TelegramHandler

from .minecraft_server import get_minecraft_server


@lru_cache
def get_telegram_handler() -> "TelegramHandler":
    return TelegramHandler(minecraft_server=get_minecraft_server())
