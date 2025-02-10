import asyncio
from typing import TYPE_CHECKING

from aiogram import Router, Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .minecraft import MinecraftServer
from .config import config
from .validators import validate_console

if TYPE_CHECKING:
    from aiogram.types import Message

router = Router()
bot = Bot(
    token=config.telegram.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dispatcher = Dispatcher()
dispatcher.include_router(router)


async def handler() -> None:
    await dispatcher.start_polling(bot)


# @router.message(Command("start"))
# @validate_console()
# async def command_start(message: "Message") -> None:
#     await message.answer("Let's get started")


@router.message(Command("help"))
@validate_console()
async def command_help(message: "Message") -> None:
    await message.answer(
        "ℹ️ Доступные команды:\n"
        "/launch — запускает сервер\n"
        "/status — проверяет, запущен ли сервер\n"
        "/terminate — выключает сервер (требуются права администратора)"
        "/help — выводит список доступных команд"
    )


@router.message(Command("launch"))
@validate_console()
async def command_launch(message: "Message") -> None:
    await message.answer("⏳ Начинается запуск сервера, ожидайте...")
    minecraft_server = MinecraftServer()
    minecraft_server.launch()
    await asyncio.sleep(6)
    await message.answer("✅ Сервер запущен, приятной игры!")


@router.message(Command("terminate"))
@validate_console()
async def command_terminate(message: "Message") -> None:
    if message.from_user:
        user = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if isinstance(user, (ChatMemberAdministrator, ChatMemberOwner)):
            await message.answer("⏳ Завершается работа сервера...")
            minecraft_server = MinecraftServer()
            await minecraft_server.terminate()
            await message.answer("✅ Сервер выключен.")
        else:
            await message.answer(
                "⚠️ У Вас нет прав на использование этой команды",
            )
    else:
        await message.answer("⚠️ У Вас нет прав на использование этой команды")


@router.message(Command("status"))
@validate_console()
async def commant_status(message: "Message") -> None:
    minecraft_server = MinecraftServer()
    await message.answer(f"Статус сервера: {minecraft_server.status()}")


@router.message(Command("list"))
@validate_console()
async def command_list(message: "Message") -> None:
    minecraft_server = MinecraftServer()
    if minecraft_server.status().startswith("Active"):
        output = await minecraft_server.list()
        if output == "0":
            await message.answer("В данный момент сервер пуст.")
        else:
            await message.answer(f"✅ Игроков на сервере: {output}.")
    else:
        await message.answer("⚠️ В данный момент сервер не работает.")


@router.message()
@validate_console()
async def command_invalid(message: "Message") -> None:
    await message.answer(
        "⚠️ Неизвестная команда: "
        f"{message.text}\n"
        "ℹ️ Введите /help, чтобы получить список доступных команд"
    )
