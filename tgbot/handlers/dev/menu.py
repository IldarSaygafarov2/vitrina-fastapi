from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from infrastructure.database.repo.requests import RequestsRepo

from backend.app.config import config
from backend.core.interfaces.advertisement import AdvertisementForReportDTO
from tgbot.misc.common import DevStates
from tgbot.utils.helpers import download_advertisement_photo
from pathlib import Path

from tgbot.utils.image_checker import is_duplicate

dev_router = Router()

@dev_router.message(CommandStart(), F.chat.id == config.tg_bot.test_main_chat_id)
async def dev_start(message: types.Message,  repo: RequestsRepo):
    await message.answer("отправь фотографию для проверки")


@dev_router.message(F.chat.id == config.tg_bot.test_main_chat_id, F.photo)
async def get_photo(message: types.Message, repo: RequestsRepo):
    upload_dir = Path("media")
    file_id = message.photo[-1].file_id
    file_location = await download_advertisement_photo(message.bot, file_id, upload_dir)

    duplicates = await is_duplicate(file_location, repo)

    if duplicates:
        pass
