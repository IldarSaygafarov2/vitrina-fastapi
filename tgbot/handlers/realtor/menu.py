from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.role import RoleFilter
from tgbot.keyboards.user.inline import realtor_start_kb, operation_type_kb
from tgbot.misc.user_states import AdvertisementCreationState
from tgbot.templates.advertisement_creation import choose_operation_type_text

router = Router()
router.message.filter(RoleFilter(role='realtor'))


@router.message(CommandStart())
async def start(message: Message, repo: RequestsRepo):
    username = message.from_user.username
    chat_id = message.from_user.id

    await repo.users.update_user_chat_id(
        tg_username=username,
        tg_chat_id=chat_id,
    )

    await message.answer(
        f"Привет, {username.title()}",
        reply_markup=realtor_start_kb(realtor_chat_id=chat_id),
    )


@router.callback_query(F.data.startswith("create_advertisement"))
async def create_advertisement(
    call: CallbackQuery,
    repo: RequestsRepo,
    state: FSMContext,
):
    await call.answer()
    await state.set_state(AdvertisementCreationState.operation_type)
    await call.message.edit_text(
        text=choose_operation_type_text(),
        reply_markup=operation_type_kb(),
    )
