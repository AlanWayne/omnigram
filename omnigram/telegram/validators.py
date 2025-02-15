# mypy: ignore-errors
from functools import wraps

from aiogram.types import Message, ChatMemberAdministrator, ChatMemberOwner

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


def validate_admin():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, message: "Message", *args, **kwargs):
            if message.from_user:
                user = await self.bot.get_chat_member(message.chat.id, message.from_user.id)
                if isinstance(user, (ChatMemberAdministrator, ChatMemberOwner)):
                    return await func(self, message, *args, **kwargs)
            response = await message.answer("⚠️ У Вас нет прав на использование этой команды")
            self.save_messages(response)

        return wrapper

    return decorator
