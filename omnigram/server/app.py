from aiogram import Dispatcher

from omnigram.factory import get_telegram_handler
from omnigram.telegram import TelegramHandler


async def serve() -> None:
    dispatcher: "Dispatcher" = Dispatcher()
    telegram_handler: "TelegramHandler" = get_telegram_handler()
    telegram_handler.register(dispatcher=dispatcher)
    await dispatcher.start_polling(telegram_handler.bot)
