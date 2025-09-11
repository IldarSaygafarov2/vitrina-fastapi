from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from infrastructure.database.repo.requests import RequestsRepo

from backend.app.config import config
from tgbot.misc.common import DevStates
from tgbot.templates.messages import rent_channel_advertisement_message

dev_router = Router()

@dev_router.message(CommandStart(), F.chat.id == config.tg_bot.test_main_chat_id)
async def dev_start(message: types.Message, state: FSMContext, repo: RequestsRepo):
    advertisement = await repo.advertisements.get_advertisement_by_unique_id('920516')
    text = rent_channel_advertisement_message(advertisement) # type: ignore
    await message.answer(text, parse_mode='HTML', disable_web_page_preview=True)



# @dev_router.message(CommandStart(), F.chat.id == config.tg_bot.test_main_chat_id)
# async def dev_start(message: types.Message, state: FSMContext):
#     await message.answer('Отправьте несколько фотографий')
#     await state.set_state(DevStates.photos)
#     await state.update_data(photos=[])
#
#
# @dev_router.message(DevStates.photos)
# async def get_photos(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     data['photos'].append(message.photo[-1].file_id)
#     await state.set_state(DevStates.title)
#     await message.answer('write something')
#
#
# @dev_router.message(DevStates.title)
# async def title(message: types.Message, state: FSMContext):
#     state_data = await state.get_data()
#
#     for photo in state_data['photos']:
#         await message.answer_photo(photo)
