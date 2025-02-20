from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.keyboards.admin.inline import admin_start_kb
from tgbot.keyboards.user.inline import realtor_advertisements_kb, realtor_start_kb

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
        if call.message.content_type == ContentType.PHOTO:
            await call.message.delete()
            return await call.bot.send_message(
                chat_id,
                text=f"""Привет, руководитель группы

Выберите действие снизу    
    """,
                reply_markup=admin_start_kb(),
            )

        return await call.message.edit_text(
            f"""Привет, руководитель группы

Выберите действие снизу    
    """,
            reply_markup=admin_start_kb(),
        )


@router.callback_query(F.data.startswith("next_page"))
async def next_page(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):

    state_data = await state.get_data()
    for_admin = state_data.get("for_admin", False)

    _, start, finish, page, total_pages = call.data.split(":")

    if int(page) == int(total_pages):
        return await call.answer("Это последняя страница", show_alert=True)

    await call.message.edit_reply_markup(
        reply_markup=realtor_advertisements_kb(
            advertisements=state_data["advertisements"],
            start=int(start) + 15,
            finish=int(finish) + 15,
            page=int(page) + 1,
            for_admin=for_admin,
        )
    )


@router.callback_query(F.data.startswith("prev_page"))
async def prev_page(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    for_admin = state_data.get("for_admin", False)

    _, start, finish, page = call.data.split(":")

    if int(page) == 1:
        return await call.answer("Это первая страница", show_alert=True)

    await call.message.edit_reply_markup(
        reply_markup=realtor_advertisements_kb(
            advertisements=state_data["advertisements"],
            start=int(start) - 15,
            finish=int(finish) - 15,
            page=int(page) - 1,
            for_admin=for_admin,
        )
    )
