from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from tgbot.keyboards.user.inline import realtor_start_kb
from tgbot.keyboards.admin.inline import admin_start_kb
from aiogram.fsm.context import FSMContext
from infrastructure.database.repo.requests import RequestsRepo

router = Router()


@router.callback_query(F.data.contains("return_home"))
async def return_home(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    await state.clear()

    username = call.message.chat.username
    chat_id = call.message.chat.id

    user = await repo.users.get_user_by_chat_id(tg_chat_id=chat_id)

    if user.role.value == "realtor":
        return await call.message.edit_text(
            f"Привет, {username.title()}",
            reply_markup=realtor_start_kb(realtor_chat_id=chat_id),
        )
    if user.role.value == "group_director":
        await call.message.edit_text(
            f"""Привет, руководитель группы

Выберите действие снизу    
    """,
            reply_markup=admin_start_kb(),
        )
