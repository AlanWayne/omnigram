# mypy: ignore-errors
from functools import wraps

from aiogram.types import Message

from omnigram.config import config


def validate_console():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, message: "Message", *args, **kwargs):
            if message.message_thread_id == config.telegram.topic_mc_console:
                return await func(self, message, *args, **kwargs)

        return wrapper

    return decorator


def validate_minecraft_chat():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, message: "Message", *args, **kwargs):
            if message.message_thread_id == config.telegram.topic_mc_minecraft_chat:
                return await func(self, message, *args, **kwargs)

        return wrapper

    return decorator
