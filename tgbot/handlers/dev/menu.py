from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from infrastructure.database.repo.requests import RequestsRepo

from backend.app.config import config
from backend.core.interfaces.advertisement import AdvertisementForReportDTO
from tgbot.misc.common import DevStates

dev_router = Router()

@dev_router.message(CommandStart(), F.chat.id == config.tg_bot.test_main_chat_id)
async def dev_start(message: types.Message, state: FSMContext, repo: RequestsRepo):
    await message.answer('Для заполнения отчета напиши либо слово "Аренда" либо "Покупка"')


@dev_router.message(F.text == 'Аренда', F.chat.id == config.tg_bot.test_main_chat_id)
async def fill_rent_report(message: types.Message, state: FSMContext, repo: RequestsRepo):
    objects = await repo.advertisements.get_all_moderated_advertisements()
    objects = [
        AdvertisementForReportDTO.model_validate(obj, from_attributes=True) for obj in objects
        if obj.operation_type.value == 'Аренда'
    ]



@dev_router.message(F.text == 'Покупка', F.chat.id == config.tg_bot.test_main_chat_id)
async def fill_buy_report(message: types.Message, state: FSMContext, repo: RequestsRepo):
    pass

