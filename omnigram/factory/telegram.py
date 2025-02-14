from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from omnigram.config import config
from aiogram import Router, Bot, Dispatcher

router = Router()
bot = Bot(
    token=config.telegram.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dispatcher = Dispatcher()
dispatcher.include_router(router)
