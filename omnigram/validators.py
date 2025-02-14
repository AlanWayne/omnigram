from functools import wraps

from .config import config
from aiogram.types import Message


def validate_console():
    def decorator(func):
        @wraps(func)
        async def wrapper(message: "Message", *args, **kwargs):
            if message.message_thread_id == config.telegram.topic_mc_console:
                return await func(message, *args, **kwargs)

        return wrapper

    return decorator


def validate_minecraft_chat():
    def decorator(func):
        @wraps(func)
        async def wrapper(message: "Message", *args, **kwargs):
            if (
                message.message_thread_id
                == config.telegram.topic_mc_minecraft_chat
            ):
                return await func(message, *args, **kwargs)

        return wrapper

    return decorator
