from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.role import RoleFilter
from tgbot.misc.realtor_states import RealtorCreationState
from tgbot.keyboards.admin.inline import admin_start_kb, manage_realtor_kb

router = Router()
router.message.filter(RoleFilter(role="group_director"))


@router.message(RealtorCreationState.first_name)
async def get_first_name_set_lastname(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await state.update_data(first_name=message.text)
    await state.set_state(RealtorCreationState.lastname)

    await message.answer(text="Напишите фамилию")


@router.message(RealtorCreationState.lastname)
async def get_lastname_set_phone_number(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await state.update_data(lastname=message.text)
    await state.set_state(RealtorCreationState.phone_number)

    await message.answer(text="Напишите номер телефона")


@router.message(RealtorCreationState.phone_number)
async def get_phone_number_set_tg_username(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await state.update_data(phone_number=message.text)
    await state.set_state(RealtorCreationState.tg_username)

    await message.answer(text="Напишите username без @")


@router.message(RealtorCreationState.tg_username)
async def get_tg_username_set_profile_image(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    tg_username = message.text

    user = await repo.users.create_user(
        first_name=data["first_name"],
        lastname=data["lastname"],
        phone_number=data["phone_number"],
        tg_username=tg_username,
        role="REALTOR",
    )

    user_message = f"""
Риелтор успешно добавлен:

Имя: <b>{user.first_name}</b>
Фамилия: <b>{user.lastname}</b>
Номер телефона: <b>{user.phone_number}</b>
Юзернейм: <b>{user.tg_username}</b>
    """

    await message.answer(
        text=user_message,
        reply_markup=manage_realtor_kb(realtor_id=user.id),
    )
    # await message.answer(
    #     text="Выберите действие ниже",
    #     reply_markup=admin_start_kb(),
    # )
