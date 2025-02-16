import asyncio
from typing import TYPE_CHECKING, cast

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore

from omnigram.config import config
from omnigram.database import MessageModel, get_session

from .validators import validate_admin, validate_console, validate_minecraft_chat

if TYPE_CHECKING:
    from aiogram import Dispatcher
    from aiogram.types import Message
    from sqlalchemy.orm.session import Session

    from omnigram.minecraft import MinecraftServer


class TelegramHandler:
    """
    Class for handling messages in Telegram bot
    """

    minecraft_server: "MinecraftServer"
    bot: "Bot"
    scheduler: "AsyncIOScheduler"

    def __init__(self, minecraft_server: "MinecraftServer"):
        self.bot = Bot(
            token=config.telegram.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.minecraft_server = minecraft_server
        self.minecraft_server._telegram_handler = self
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(
            self.delete_messages,
            CronTrigger(hour=0, minute=0),
        )
        self.scheduler.start()

    def register(self, dispatcher: "Dispatcher") -> None:
        """
        Registering handling methods

        :param dispatcher: aiogram "Dispatcher" model
        :return: None
        """
        dispatcher.message.register(self.command_help, Command(commands=["help"]))
        dispatcher.message.register(self.command_launch, Command(commands=["launch"]))
        dispatcher.message.register(self.command_terminate, Command(commands=["terminate"]))
        dispatcher.message.register(self.commant_status, Command(commands=["status"]))
        dispatcher.message.register(self.command_list, Command(commands=["list"]))
        dispatcher.message.register(self.command_clear, Command(commands=["clear"]))
        dispatcher.message.register(self.command_undifined)

    async def send_message_to_console(self, text: str, message: "Message | None" = None) -> None:
        messages = []
        response = await self.bot.send_message(
            chat_id=config.telegram.group_mc, message_thread_id=config.telegram.topic_mc_console, text=text
        )
        messages.append(response)
        messages.append(message) if message is not None else None
        self._save_messages(*messages)

    async def send_message_to_chat(self, text: str) -> None:
        response = await self.bot.send_message(
            chat_id=config.telegram.group_mc, message_thread_id=config.telegram.topic_mc_minecraft_chat, text=text
        )
        self._save_messages(response)

    @staticmethod
    def _save_messages(*messages: "Message", session: "Session" = next(get_session())) -> None:
        """
        Saving messages to database.

        :param messages: aiogram "Message" model tuple
        :param session: sync database session
        :return: None
        """
        for message in messages:
            message_already_exists = session.query(MessageModel).filter_by(id=message.message_id).first()
            if not message_already_exists:
                user_id = message.from_user.id if message.from_user else None
                item: MessageModel = MessageModel(
                    id=message.message_id,
                    chat_id=message.chat.id,
                    user_id=user_id,
                    text=message.text,
                    timestamp=message.date,
                )
                session.add(item)
                session.commit()

    async def delete_messages(self, session: "Session" = next(get_session())) -> None:
        """
        Deleting messages from console-chat, logic deleting from the database.

        :param session: sync database session
        :return: None
        """
        messages = session.query(MessageModel).filter(MessageModel.deleted.is_(False)).all()
        for message in messages:
            try:
                await self.bot.delete_message(chat_id=cast(int, message.chat_id), message_id=cast(int, message.id))
            except Exception as e:
                print("Message delete:", e)
        session.query(MessageModel).filter(~MessageModel.deleted).update({MessageModel.deleted: True})
        session.commit()

    @validate_console()
    async def command_help(self, message: "Message") -> None:
        """
        Helm command handler.

        :param message: aiogram "Message" model
        :return: None
        """
        text = (
            "ℹ️ Доступные команды:\n"
            "/launch — запускает сервер;\n"
            "/status — проверяет, запущен ли сервер;\n"
            "/list — выводит количество людей, играющих на сервере в данный момент;\n"
            "/terminate — выключает сервер (требуются права администратора);\n"
            "/clear — удаляет все сообщения в чате;\n"
            "/help — выводит список доступных команд;"
        )
        await self.send_message_to_console(message=message, text=text)

    @validate_console()
    async def command_launch(self, message: "Message") -> None:
        """
        Launch command handler.

        :param message: aiogram "Message" model
        :return: None
        """
        await self.send_message_to_console(message=message, text="⏳ Начинается запуск сервера, ожидайте...")
        self.minecraft_server.launch()
        await asyncio.sleep(6)
        await self.send_message_to_console(message=message, text="✅ Сервер запущен, приятной игры!")

    @validate_console()
    @validate_admin()
    async def command_terminate(self, message: "Message") -> None:
        """
        Terminate command handler - Admin rights are mandated

        :param message: aiogram "Message" model
        :return: None
        """
        await self.send_message_to_console(message=message, text="⏳ Завершается работа сервера...")
        await self.minecraft_server.command_terminate()
        await self.send_message_to_console(message=message, text="✅ Сервер выключен.")

    @validate_console()
    async def commant_status(self, message: "Message") -> None:
        """
        Status command handler.

        :param message: aiogram "Message" model
        :return: None
        """
        await self.send_message_to_console(message=message, text=f"Статус сервера: {self.minecraft_server.status()}")

    @validate_console()
    async def command_list(self, message: "Message") -> None:
        """
        List command handler. Lists number of people online.

        :param message: aiogram "Message" model
        :return: None
        """
        if self.minecraft_server.status().startswith("Active"):
            output = await self.minecraft_server.list()
            if output == "0" or output is None:
                await self.send_message_to_console(message=message, text="👻 В данный момент сервер пуст.")
            else:
                await self.send_message_to_console(message=message, text=f"✅ Игроков на сервере: {output}.")
        else:
            await self.send_message_to_console(message=message, text="⚠️ В данный момент сервер не работает.")

    @validate_console()
    async def command_clear(self, message: "Message") -> None:
        """
        Clear command handler. Clears the console chat - sheduled by exact time and on bot start.

        :param message: aiogram "Message" model
        :return: None
        """
        await self.delete_messages()
        await message.delete()

    async def command_undifined(self, message: "Message") -> None:
        """
        Undefined command handler. Redirecting to another function.

        :param message: aiogram "Message" model
        :return: None
        """
        if message.message_thread_id == config.telegram.topic_mc_console:
            return await self.command_invalid(message=message)
        elif message.message_thread_id == config.telegram.topic_mc_minecraft_chat:
            return await self.minecraft_chat_listener(message=message)

    @validate_minecraft_chat()
    async def minecraft_chat_listener(self, message: "Message") -> None:
        """
        Telegram-minecraft chat sub-handler.

        :param message: aiogram "Message" model
        :return: None
        """
        if message.from_user is not None:
            user = message.from_user.full_name
            text = message.text
            if text is not None:
                if self.minecraft_server.status().startswith("Active"):
                    await self.minecraft_server.send_message_to_minecraft(user=user, text=text)
                else:
                    await message.answer("⚠️ В данный момент сервер не работает.")

    @validate_console()
    async def command_invalid(self, message: "Message") -> None:
        """
        Invalid command sub-handler.

        :param message: aiogram "Message" model
        :return: None
        """
        await self.send_message_to_console(
            message=message,
            text=f"⚠️ Неизвестная команда: {message.text}\nℹ️ Введите /help, чтобыполучить список доступных команд",
        )
