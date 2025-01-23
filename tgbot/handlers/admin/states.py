from pathlib import Path
import shutil

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.role import RoleFilter
from tgbot.keyboards.admin.inline import manage_realtor_kb
from tgbot.misc.realtor_states import RealtorCreationState

router = Router()
router.message.filter(RoleFilter(role="group_director"))


upload_dir = Path("media")
upload_dir.mkdir(parents=True, exist_ok=True)


@router.message(RealtorCreationState.first_name)
async def get_first_name_set_lastname(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    chat_id = message.from_user.id

    await state.update_data(first_name=message.text, chat_id=chat_id)
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

    await state.set_state(RealtorCreationState.photo)
    await state.update_data(tg_username=message.text)

    await message.answer("Отправьте фото агента")


@router.message(RealtorCreationState.photo, F.content_type == ContentType.PHOTO)
async def get_profile_image_create_user(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()

    photo_id = message.photo[-1].file_id

    file_obj = await message.bot.get_file(photo_id)
    filename = file_obj.file_path.split("/")[-1]
    file = await message.bot.download_file(file_obj.file_path)

    user_image_folder = upload_dir / "users"
    user_image_folder.mkdir(parents=True, exist_ok=True)

    file_location = user_image_folder / filename

    with open(file_location, "wb") as f:
        shutil.copyfileobj(file, f)

    user = await repo.users.create_user(
        first_name=data["first_name"],
        lastname=data["lastname"],
        phone_number=data["phone_number"],
        tg_username=data["tg_username"],
        profile_image=str(file_location),
        profile_image_hash=photo_id,
        role="REALTOR",
        added_by=data["chat_id"],
    )

    user_message = f"""
Риелтор успешно добавлен:

Имя: <b>{user.first_name}</b>
Фамилия: <b>{user.lastname}</b>
Номер телефона: <b>{user.phone_number}</b>
Юзернейм: <b>{user.tg_username}</b>
    """

    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=photo_id,
        caption=user_message,
        reply_markup=manage_realtor_kb(realtor_id=user.id),
    )
