import asyncio
from typing import TYPE_CHECKING

from aiogram.filters import Command
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore

from .config import config
from .database.config import get_session
from .minecraft import MinecraftServer
from .validators import validate_console, validate_minecraft_chat
from omnigram.database.config import MessageModel
from omnigram.factory.telegram import dispatcher, bot, router

if TYPE_CHECKING:
    from aiogram.types import Message
    from sqlalchemy.orm.session import Session


async def handler() -> None:
    await delete_messages()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        delete_messages,
        CronTrigger(hour=0, minute=0),
    )
    scheduler.start()
    await dispatcher.start_polling(bot)


def save_message(
    message: "Message", session: "Session" = next(get_session())
) -> None:
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


async def delete_messages(session: "Session" = next(get_session())) -> None:
    messages = (
        session.query(MessageModel)
        .filter(MessageModel.deleted.is_(False))
        .all()
    )

    for message in messages:
        try:
            await bot.delete_message(
                chat_id=int(message.chat_id), message_id=int(message.id)
            )
        except Exception as e:
            print("Message delete:", e)

    session.query(MessageModel).filter(~MessageModel.deleted).update(
        {MessageModel.deleted: True}
    )
    session.commit()


@router.message(Command("help"))
@validate_console()
async def command_help(message: "Message") -> None:
    response = await message.answer(
        "ℹ️ Доступные команды:\n"
        "/launch — запускает сервер. Реализован по принципу Singleton, так что"
        " при повторном запуске ошибок быть не должно;\n"
        "/status — проверяет, запущен ли сервер;\n"
        "/list — выводит количество людей, играющих на сервере в данный момент"
        ";\n"
        "/terminate — выключает сервер (требуются права администратора);\n"
        "/clear — удаляет все сообщения в чате;\n"
        "/help — выводит список доступных команд;"
    )
    save_message(message)
    save_message(response)


@router.message(Command("launch"))
@validate_console()
async def command_launch(message: "Message") -> None:
    response1 = await message.answer(
        "⏳ Начинается запуск сервера, ожидайте..."
    )
    minecraft_server = MinecraftServer()
    minecraft_server.launch()
    await asyncio.sleep(6)
    response2 = await message.answer("✅ Сервер запущен, приятной игры!")

    save_message(message)
    save_message(response1)
    save_message(response2)


@router.message(Command("terminate"))
@validate_console()
async def command_terminate(message: "Message") -> None:
    if message.from_user:
        user = await bot.get_chat_member(message.chat.id, message.from_user.id)

        if isinstance(user, (ChatMemberAdministrator, ChatMemberOwner)):
            response1 = await message.answer(
                "⏳ Завершается работа сервера..."
            )
            minecraft_server = MinecraftServer()
            await minecraft_server.terminate()
            response2 = await message.answer("✅ Сервер выключен.")

            save_message(response1)
            save_message(response2)

        else:
            response = await message.answer(
                "⚠️ У Вас нет прав на использование этой команды",
            )

            save_message(response)
    else:
        response = await message.answer(
            "⚠️ У Вас нет прав на использование этой команды"
        )

        save_message(response)

    save_message(message)


@router.message(Command("status"))
@validate_console()
async def commant_status(message: "Message") -> None:
    minecraft_server = MinecraftServer()
    response = await message.answer(
        f"Статус сервера: {minecraft_server.status()}"
    )

    save_message(message)
    save_message(response)


@router.message(Command("list"))
@validate_console()
async def command_list(message: "Message") -> None:
    minecraft_server = MinecraftServer()

    if minecraft_server.status().startswith("Active"):
        output = await minecraft_server.list()

        if output == "0" or output is None:
            response = await message.answer("👻 В данный момент сервер пуст.")

        else:
            response = await message.answer(
                f"✅ Игроков на сервере: {output}."
            )

    else:
        response = await message.answer(
            "⚠️ В данный момент сервер не работает."
        )

    save_message(message)
    save_message(response)


@router.message(Command("clear"))
@validate_console()
async def command_clear(message: "Message") -> None:
    await delete_messages()
    await message.delete()


@router.message()
async def not_a_command(message: "Message") -> None:
    if message.message_thread_id == config.telegram.topic_mc_console:
        return await command_invalid(message=message)
    elif message.message_thread_id == config.telegram.topic_mc_minecraft_chat:
        return await minecraft_chat_listener(message=message)


@validate_minecraft_chat()
async def minecraft_chat_listener(message: "Message") -> None:
    if message.from_user is not None:
        user = message.from_user.full_name
        text = message.text

        if text is not None:
            minecraft_server = MinecraftServer()
            if minecraft_server.status().startswith("Active"):
                await minecraft_server.send_message_to_minecraft(
                    user=user, text=text
                )
            else:
                await message.answer("⚠️ В данный момент сервер не работает.")


@validate_console()
async def command_invalid(message: "Message") -> None:
    response = await message.answer(
        f"⚠️ Неизвестная команда: {message.text}\nℹ️ Введите /help, чтобы"
        f"получить список доступных команд"
    )

    save_message(message)
    save_message(response)
