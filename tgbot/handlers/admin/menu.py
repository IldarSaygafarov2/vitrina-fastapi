import os
import shutil
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.role import RoleFilter
from tgbot.keyboards.admin.inline import (
    admin_start_kb,
    confirm_realtor_delete_kb,
    delete_advertisement_kb,
    manage_realtor_kb,
    realtor_fields_kb,
    realtors_actions_kb,
    realtors_kb,
    directors_kb,
)
from tgbot.keyboards.user.inline import realtor_advertisements_kb
from tgbot.misc.realtor_states import RealtorCreationState, RealtorUpdatingState
from tgbot.misc.user_states import (
    AdvertisementDeletionState,
    AdvertisementModerationState,
)
from tgbot.templates.advertisement_creation import realtor_advertisement_completed_text
from tgbot.templates.messages import (
    rent_channel_advertisement_message,
    buy_channel_advertisement_message,
)
from tgbot.templates.realtor_texts import get_realtor_info
from tgbot.utils.helpers import get_media_group

router = Router()
router.message.filter(RoleFilter(role="group_director"))
router.callback_query.filter(RoleFilter(role="group_director"))

upload_dir = Path("media")
upload_dir.mkdir(parents=True, exist_ok=True)

config = load_config()


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

    director = await repo.users.get_user_by_chat_id(tg_chat_id=call.from_user.id)
    if not director.is_superadmin:
        realtors = await repo.users.get_director_agents(
            director_chat_id=call.from_user.id
        )
    else:
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

    advertisements = await repo.advertisements.get_user_advertisements(
        user_id=realtor.id
    )

    await state.update_data(advertisements=advertisements)

    realtor_info = get_realtor_info(realtor)

    profile_image = (
        realtor.profile_image_hash
        if realtor.profile_image_hash
        else "https://cdn.vectorstock.com/i/500p/08/19/gray-photo-placeholder-icon-design-ui-vector-35850819.jpg"
    )
    await call.message.delete()
    await call.message.answer_photo(
        photo=profile_image,
        caption=realtor_info,
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

    await call.message.answer(
        text=f"Вы действительно хотите удалить агента: <b>{realtor.first_name} {realtor.lastname}</b>",
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
        text="Агент успешно удален",
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
    await state.update_data(for_admin=True)
    await call.message.delete()
    await call.message.answer(
        text=f"Объявления агента: <b>{realtor.first_name} {realtor.lastname}</b>",
        reply_markup=realtor_advertisements_kb(
            advertisements=advertisements, for_admin=True
        ),
    )


@router.callback_query(F.data.startswith("rg_realtor_advertisement"))
async def get_realtor_advertisement(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    advertisement_message = realtor_advertisement_completed_text(advertisement)
    photos = [obj.tg_image_hash for obj in advertisement.images]

    try:
        if all(photos):
            media_group = get_media_group(photos, advertisement_message)
        else:
            media_group = []

        if media_group:
            await call.message.answer_media_group(
                media=media_group,
                reply_markup=delete_advertisement_kb(advertisement_id),
            )
            return await call.message.answer(
                text="Выберите действие над объявлением",
                reply_markup=delete_advertisement_kb(advertisement_id),
            )

        return await call.message.edit_text(
            text=advertisement_message,
            reply_markup=delete_advertisement_kb(advertisement_id),
        )
    except Exception as e:
        return await call.bot.send_message(chat_id=5090318438, text=str(e))


@router.callback_query(F.data.startswith("edit_realtor"))
async def edit_realtor_data(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    director = await repo.users.get_user_by_chat_id(tg_chat_id=call.from_user.id)

    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    await call.message.edit_caption(
        caption=get_realtor_info(realtor),
        reply_markup=realtor_fields_kb(
            realtor_id, is_superadmin=director.is_superadmin
        ),
    )


@router.callback_query(F.data.startswith("update_realtor_director"))
async def update_realtor_director(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    realtor_id = int(call.data.split(":")[-1])

    current_director = await repo.users.get_user_by_chat_id(
        tg_chat_id=call.from_user.id
    )

    directors = await repo.users.get_users_by_role(role="GROUP_DIRECTOR")

    await call.message.edit_caption(
        caption="Выберите руководителя",
        reply_markup=directors_kb(
            directors=directors, current_director=current_director
        ),
    )
    await state.update_data(realtor_id=realtor_id, current_director=current_director)


@router.callback_query(F.data.startswith("select_director"))
async def select_director_for_agent(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()
    data = await state.get_data()
    call_data = call.data.split(":")
    director_chat_id = call_data[-1]

    updated = await repo.users.update_user(
        user_id=data["realtor_id"],
        added_by=int(director_chat_id),
    )
    await call.message.edit_caption(
        caption=get_realtor_info(updated),
        reply_markup=realtors_actions_kb(),
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

    cur_message = await call.message.edit_caption(
        caption=f"Имя агента: <b>{realtor.first_name}</b>\nВведите новое имя агента:",
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
    await cur_message.edit_caption(
        caption=get_realtor_info(updated),
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

    cur_message = await call.message.edit_caption(
        caption=f"Фамилия агента: <b>{realtor.first_name}</b>\nВведите новую фамилию агента:",
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
    await cur_message.edit_caption(
        caption=get_realtor_info(updated),
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

    cur_message = await call.message.edit_caption(
        caption=f"Номер телефона агента: <b>{realtor.first_name}</b>\nВведите новый номер телефона агента:",
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
    await cur_message.edit_caption(
        caption=get_realtor_info(updated),
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

    cur_message = await call.message.edit_caption(
        caption=f"Юзернейм агента: <b>{realtor.first_name}</b>\nВведите новый юзернейм агента:",
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
    await cur_message.edit_caption(
        caption=get_realtor_info(updated),
        reply_markup=realtor_fields_kb(realtor_id),
    )

    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith("update_realtor_photo"))
async def update_profile_image(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    cur_message = await call.message.edit_caption(
        caption="Отправьте новую фотографию профиля", reply_markup=None
    )
    await state.set_state(RealtorUpdatingState.photo)
    await state.update_data(realtor_id=realtor_id, cur_message=cur_message)


@router.message(RealtorUpdatingState.photo, F.content_type == ContentType.PHOTO)
async def update_profile_image(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    data = await state.get_data()
    realtor_id = data.get("realtor_id")
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)
    cur_message = data.get("cur_message")

    if realtor.profile_image:
        os.remove(realtor.profile_image)

    photo_id = message.photo[-1].file_id
    file_obj = await message.bot.get_file(photo_id)
    filename = file_obj.file_path.split("/")[-1]
    file = await message.bot.download_file(file_obj.file_path)

    user_image_folder = upload_dir / "users"
    user_image_folder.mkdir(parents=True, exist_ok=True)

    file_location = user_image_folder / filename

    with open(file_location, "wb") as f:
        shutil.copyfileobj(file, f)

    updated = await repo.users.update_user(
        user_id=realtor_id,
        profile_image=str(file_location),
        profile_image_hash=photo_id,
    )

    await cur_message.delete()
    await state.clear()
    await message.delete()

    await message.answer_photo(
        photo=photo_id,
        caption=get_realtor_info(updated),
        reply_markup=realtor_fields_kb(realtor_id),
    )


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

    photos = [obj.tg_image_hash for obj in advertisement.images]

    user = await repo.users.get_user_by_id(user_id=advertisement.user_id)

    if advertisement.operation_type.value == "Аренда":
        chat_id = config.tg_bot.rent_channel_name
        advertisement_message = rent_channel_advertisement_message(advertisement)
    else:
        chat_id = config.tg_bot.buy_channel_name
        advertisement_message = buy_channel_advertisement_message(advertisement)

    media_group = get_media_group(photos, advertisement_message)
    try:
        await call.bot.send_media_group(
            chat_id=chat_id,
            media=media_group,
        )
    except Exception as e:
        return await call.bot.send_message(chat_id=5090318438, text=str(e))
    await call.message.edit_text("Спасибо! Объявление отправлено в канал")

    await call.bot.send_message(
        chat_id=user.tg_chat_id, text="Объявление прошло модерацию"
    )

    await call.message.delete()


@router.callback_query(F.data.startswith("moderation_deny"))
async def process_moderation_deny(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        await call.answer()

        advertisement_id = int(call.data.split(":")[-1])

        advertisement = await repo.advertisements.update_advertisement(
            advertisement_id=advertisement_id, is_moderated=False
        )
        user = await repo.users.get_user_by_id(user_id=advertisement.user_id)

        await state.update_data(user=user, advertisement=advertisement)
        await state.set_state(AdvertisementModerationState.message)

        await call.message.edit_text(
            "Напишите причину, почему данное объявление не прошло модерацию",
            reply_markup=None,
        )
    except Exception as e:
        await call.bot.send_message(chat_id=5090318438, text=str(e))


@router.message(AdvertisementModerationState.message)
async def process_moderation_deny_message(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        data = await state.get_data()
        user = data.pop("user")
        advertisement = data.pop("advertisement")

        await message.bot.send_message(
            chat_id=user.tg_chat_id,
            text=f"Объявление <b>{advertisement.name}</b> не прошло модерацию",
        )
        await message.bot.send_message(chat_id=user.tg_chat_id, text=message.text)
        await state.clear()
    except Exception as e:
        await message.bot.send_message(chat_id=5090318438, text=str(e))


@router.callback_query(F.data.startswith("rg_advertisement_delete"))
async def delete_realtor_advertisement(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    user_id = advertisement.user_id

    user = await repo.users.get_user_by_id(user_id)

    await call.bot.send_message(
        user.tg_chat_id, f"Объявление {advertisement.name} было удалено"
    )
    await call.message.answer("Объявление успешно удалено")
    await repo.advertisements.delete_advertisement(advertisement_id)


# confirm_advertisement_delete
# deny_advertisement_delete


@router.callback_query(F.data.startswith("confirm_advertisement_delete"))
async def confirm_advertisement_delete(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    user_id = advertisement.user_id

    user = await repo.users.get_user_by_id(user_id)

    await call.bot.send_message(
        user.tg_chat_id,
        f"Объявление {advertisement.name} {advertisement.unique_id} было удалено",
    )
    await call.message.answer("Объявление успешно удалено")
    await repo.advertisements.delete_advertisement(advertisement_id)


@router.callback_query(F.data.startswith("deny_advertisement_delete"))
async def deny_advertisement_delete(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await call.message.answer("напишите причину отказа")
    await state.set_state(AdvertisementDeletionState.message)
    await state.update_data(advertisement=advertisement)


@router.message(AdvertisementDeletionState.message)
async def process_advertisement_deletion_message(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    data = await state.get_data()
    advertisement = data.pop("advertisement")

    user = await repo.users.get_user_by_id(user_id=advertisement.user_id)
    await message.bot.send_message(
        user.tg_chat_id,
        f"Объявление {advertisement.name} {advertisement.unique_id} не было удалено",
    )
    await message.bot.send_message(user.tg_chat_id, f"Причина: {message.text}")
    await state.clear()


@router.callback_query(F.data.startswith("for_base_channel"))
async def get_advertisement_for_base_channel(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    user = await repo.users.get_user_by_id(user_id=advertisement.user_id)

    chat_id = config.tg_bot.base_channel_name
    photos = [obj.tg_image_hash for obj in advertisement.images]

    if advertisement.operation_type.value == "Аренда":
        advertisement_message = rent_channel_advertisement_message(advertisement)
    else:
        advertisement_message = buy_channel_advertisement_message(advertisement)

    media_group = get_media_group(photos, advertisement_message)

    try:
        await call.bot.send_media_group(
            chat_id=chat_id,
            media=media_group,
        )
    except Exception as e:
        return await call.bot.send_message(chat_id=config.tg_bot.main_chat_id, text=str(e))

    await call.message.edit_text("Спасибо! Объявление отправлено в резервный канал")
    await call.bot.send_message(
        chat_id=user.tg_chat_id, text="Объявление отправлено в резервный канал"
    )
    await call.message.delete()
