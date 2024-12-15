from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.role import RoleFilter
from tgbot.keyboards.admin.inline import (
    admin_start_kb,
    confirm_realtor_delete_kb,
    manage_realtor_kb,
    realtor_fields_kb,
    realtors_actions_kb,
    realtors_kb,
)
from tgbot.keyboards.user.inline import realtor_advertisements_kb, return_home_kb
from tgbot.misc.realtor_states import RealtorCreationState, RealtorUpdatingState
from tgbot.misc.user_states import AdvertisementModerationState
from tgbot.templates.advertisement_creation import realtor_advertisement_completed_text
from tgbot.templates.realtor_texts import get_realtor_info

router = Router()
router.message.filter(RoleFilter(role="group_director"))
router.callback_query.filter(RoleFilter(role="group_director"))


@router.message(CommandStart())
async def start(message: Message, repo: "RequestsRepo"):
    username = message.from_user.username
    chat_id = message.from_user.id
    await repo.users.update_user_chat_id(
        tg_username=username,
        tg_chat_id=chat_id,
    )
    await message.answer(
        f"""Привет, руководитель группы

Выберите действие снизу    
    """,
        reply_markup=admin_start_kb(),
    )


@router.callback_query(F.data == "rg_realtors")
async def get_realtors(
    call: CallbackQuery,
    repo: "RequestsRepo",
):
    await call.answer()

    await call.message.edit_text(
        text="Выберите действие ниже",
        reply_markup=realtors_actions_kb(),
    )


@router.callback_query(F.data == "rg_realtors_all")
async def get_all_realtors(
    call: CallbackQuery,
    repo: "RequestsRepo",
):
    await call.answer()

    realtors = await repo.users.get_users_by_role(role="REALTOR")
    await call.message.edit_text(
        text="Список риелторов",
        reply_markup=realtors_kb(realtors=realtors),
    )


@router.callback_query(F.data == "rg_realtors_add")
async def add_new_realtor(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    await call.message.edit_text(text="Напишите имя", reply_markup=None)
    await state.set_state(RealtorCreationState.first_name)


@router.callback_query(F.data.startswith("get_realtor"))
async def get_realtor(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    realtor_id = int(call.data.split(":")[-1])

    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    realtor_info = get_realtor_info(realtor)

    await call.message.edit_text(
        text=realtor_info,
        reply_markup=manage_realtor_kb(realtor_id=realtor_id),
    )


@router.callback_query(F.data.startswith("delete_realtor"))
async def delete_reltor(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    await call.message.edit_text(
        text=f"Вы действительно хотите удалить риелтора: <b>{realtor.first_name} {realtor.lastname}</b>",
        reply_markup=confirm_realtor_delete_kb(realtor_id=realtor_id),
    )


@router.callback_query(F.data.startswith("confirm_delete"))
async def confirm_realtor_delete(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    await repo.users.delete_user(user_id=realtor_id)

    realtors = await repo.users.get_users_by_role(role="REALTOR")
    await call.message.edit_text(
        text="Риелтор успешно удален",
        reply_markup=realtors_kb(realtors=realtors),
    )


@router.callback_query(F.data.startswith("realtor_advertisements"))
async def get_realtor_advertisements(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    advertisements = await repo.advertisements.get_user_advertisements(
        user_id=realtor_id
    )

    await call.message.edit_text(
        text=f"Объявления риелтора: <b>{realtor.first_name} {realtor.lastname}</b>",
        reply_markup=realtor_advertisements_kb(
            advertisements=advertisements, for_admin=True
        ),
    )


@router.callback_query(F.data.startswith("rg_realtor_advertisement"))
async def get_realtor_advertisements(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    advertisement_message = realtor_advertisement_completed_text(advertisement)

    await call.message.edit_text(
        text=advertisement_message,
        reply_markup=return_home_kb(),
    )


@router.callback_query(F.data.startswith("edit_realtor"))
async def edit_realtor_data(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    await call.message.edit_text(
        text=get_realtor_info(realtor),
        reply_markup=realtor_fields_kb(realtor_id),
    )


@router.callback_query(F.data.startswith("update_name"))
async def update_name(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    cur_message = await call.message.edit_text(
        text=f"Имя риелтора: <b>{realtor.first_name}</b>\nВведите новое имя риелтора:",
        reply_markup=None,
    )

    await state.update_data(realtor_id=realtor_id, realtor_message=cur_message)
    await state.set_state(RealtorUpdatingState.first_name)


@router.message(RealtorUpdatingState.first_name)
async def update_name(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    realtor_id = data.pop("realtor_id")
    cur_message = data.pop("realtor_message")

    updated = await repo.users.update_user(user_id=realtor_id, first_name=message.text)
    await cur_message.edit_text(
        text=get_realtor_info(updated),
        reply_markup=realtor_fields_kb(realtor_id),
    )

    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith("update_lastname"))
async def update_lastname(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    cur_message = await call.message.edit_text(
        text=f"Фамилия риелтора: <b>{realtor.first_name}</b>\nВведите новую фамилию риелтора:",
        reply_markup=None,
    )

    await state.update_data(realtor_id=realtor_id, realtor_message=cur_message)
    await state.set_state(RealtorUpdatingState.lastname)


@router.message(RealtorUpdatingState.lastname)
async def update_lastname(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    realtor_id = data.pop("realtor_id")
    cur_message = data.pop("realtor_message")

    updated = await repo.users.update_user(user_id=realtor_id, lastname=message.text)
    await cur_message.edit_text(
        text=get_realtor_info(updated),
        reply_markup=realtor_fields_kb(realtor_id),
    )

    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith("update_phone_number"))
async def update_phone_number(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    cur_message = await call.message.edit_text(
        text=f"Номер телефона риелтора: <b>{realtor.first_name}</b>\nВведите новый номер телефона риелтора:",
        reply_markup=None,
    )

    await state.update_data(realtor_id=realtor_id, realtor_message=cur_message)
    await state.set_state(RealtorUpdatingState.phone_number)


@router.message(RealtorUpdatingState.phone_number)
async def update_phone_number(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    realtor_id = data.pop("realtor_id")
    cur_message = data.pop("realtor_message")

    updated = await repo.users.update_user(
        user_id=realtor_id, phone_number=message.text
    )
    await cur_message.edit_text(
        text=get_realtor_info(updated),
        reply_markup=realtor_fields_kb(realtor_id),
    )

    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith("update_tg_username"))
async def update_tg_username(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    cur_message = await call.message.edit_text(
        text=f"Юзернейм риелтора: <b>{realtor.first_name}</b>\nВведите новый юзернейм риелтора:",
        reply_markup=None,
    )

    await state.update_data(realtor_id=realtor_id, realtor_message=cur_message)
    await state.set_state(RealtorUpdatingState.tg_username)


@router.message(RealtorUpdatingState.tg_username)
async def update_tg_username(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    realtor_id = data.pop("realtor_id")
    cur_message = data.pop("realtor_message")

    updated = await repo.users.update_user(user_id=realtor_id, tg_username=message.text)
    await cur_message.edit_text(
        text=get_realtor_info(updated),
        reply_markup=realtor_fields_kb(realtor_id),
    )

    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith("moderation_confirm"))
async def process_moderation_confirm(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])

    advertisement = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id, is_moderated=True
    )
    user = await repo.users.get_user_by_id(user_id=advertisement.user_id)
    await call.message.edit_text("Спасибо!")
    await call.bot.send_message(
        chat_id=user.tg_chat_id, text="Объявление прошло модерацию"
    )


@router.callback_query(F.data.startswith("moderation_deny"))
async def process_moderation_deny(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])

    advertisement = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id, is_moderated=False
    )
    user = await repo.users.get_user_by_id(user_id=advertisement.user_id)

    await state.update_data(user=user, advertisement=advertisement)
    await state.set_state(AdvertisementModerationState.message)

    await call.message.answer(
        "Напишите причину, почему данное объявление не прошло модерацию"
    )


@router.message(AdvertisementModerationState.message)
async def process_moderation_deny_message(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    user = data.pop("user")
    advertisement = data.pop("advertisement")

    await message.bot.send_message(
        chat_id=user.tg_chat_id,
        text=f"Объявление <b>{advertisement.name}</b> не прошло модерацию",
    )
    await message.bot.send_message(chat_id=user.tg_chat_id, text=message.text)
    await state.clear()
