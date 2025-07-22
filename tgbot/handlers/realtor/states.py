import shutil
from datetime import datetime
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config.loader import load_config

from infrastructure.database.models.advertisement import (
    OperationType,
    OperationTypeUz,
    PropertyType,
    PropertyTypeUz,
    RepairType,
    RepairTypeUz,
)
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.utils.helpers import generate_code
from tgbot.keyboards.admin.inline import advertisement_moderation_kb
from tgbot.keyboards.user.inline import (
    advertisement_actions_kb,
    categories_kb,
    districts_kb,
    is_studio_kb,
    property_type_kb,
    repair_type_kb,
)
from tgbot.misc.constants import (
    OPERATION_TYPE_MAPPING,
    OPERATION_TYPE_MAPPING_UZ,
    PROPERTY_TYPE_MAPPING,
    PROPERTY_TYPE_MAPPING_UZ,
    REPAIR_TYPE_MAPPING,
    REPAIR_TYPE_MAPPING_UZ,
)
from tgbot.misc.user_states import AdvertisementCreationState
from tgbot.templates.advertisement_creation import (
    choose_category_text,
    choose_photos_text,
    creation_year_text,
    get_address_text,
    get_address_text_uz,
    get_description_text,
    get_district_text,
    get_propety_type_text,
    get_title_text,
    is_studio_text,
    price_text,
    realtor_advertisement_completed_text,
)
from tgbot.utils.helpers import filter_digits, get_media_group

import logging

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Создание обработчика для записи в файл
file_handler = logging.FileHandler('logs/my_app.log')
file_handler.setLevel(logging.DEBUG)

# Создание форматировщика для определения формата логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(file_handler)

# Запись логов



router = Router()

upload_dir = Path("media")
upload_dir.mkdir(parents=True, exist_ok=True)

config = load_config()

@router.callback_query(F.data.startswith("operation_type"))
async def get_operation_type_set_category(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()
    _, operation_type = call.data.split(":")

    operation_type_text = OPERATION_TYPE_MAPPING[operation_type]

    await state.update_data(operation_type=operation_type)
    await state.set_state(AdvertisementCreationState.category)

    categories = await repo.categories.get_categories()

    await call.message.answer(
        text=choose_category_text(operation_type=operation_type_text),
        reply_markup=categories_kb(categories=categories),
    )


@router.callback_query(F.data.startswith("chosen_category"))
async def get_category_set_photos_quantity(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    category_id = int(call.data.split(":")[-1])

    category = await repo.categories.get_category_by_id(category_id=category_id)

    message = await call.message.answer(
        text="""Отправьте заставку объявления
Фотография будет отображаться на странице списка объявлений
(Не добавляйте фотографии унитазов, ванной комнаты, и других непрезентабельных комнат)
        """
    )

    await state.update_data(category=category, photos_qty_message=message)
    await state.set_state(AdvertisementCreationState.preview)


@router.message(AdvertisementCreationState.preview)
async def get_preview(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    photo_id = message.photo[-1].file_id
    await message.answer("Напишите сколько фотографий будет у объявления")
    await state.update_data(preview_file_id=photo_id)
    await state.set_state(AdvertisementCreationState.photos_quantity)


@router.message(AdvertisementCreationState.photos_quantity)
async def get_photos_quanity_set_get_photos(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    state_data = await state.get_data()

    photos_qty_message = state_data.pop("photos_qty_message")

    photos_message = await photos_qty_message.answer(
        text=choose_photos_text(photos_quantity=message.text)
    )

    await state.update_data(
        photos_quantity=int(message.text),
        photos_message=photos_message,
        photos=[],
    )
    await state.set_state(AdvertisementCreationState.photos)


@router.message(AdvertisementCreationState.photos)
async def get_photos_set_title(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    current_state = await state.get_data()
    current_state["photos"].append(message.photo[-1].file_id)

    try:
        await message.delete()
    except Exception as e:
        pass

    if current_state["photos_quantity"] == len(current_state["photos"]):
        cur_message = await message.answer(
            text=get_title_text(),
            reply_markup=None,
        )

        await state.update_data(
            photos=current_state["photos"], title_message=cur_message
        )
        await state.set_state(AdvertisementCreationState.title)


@router.message(AdvertisementCreationState.title)
async def get_title_set_description(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    state_data = await state.get_data()
    title_message = state_data.pop("title_message")

    title_message = await title_message.answer(text=get_title_text(lang="uz"))

    await state.update_data(title=message.text, title_message=title_message)
    await state.set_state(AdvertisementCreationState.title_uz)


@router.message(AdvertisementCreationState.title_uz)
async def get_title_uz(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        data = await state.get_data()
        title_message = data.pop("title_message")

        description_text = await title_message.answer(text=get_description_text())
        await state.update_data(
            title_uz=message.text, description_text=description_text
        )
        await state.set_state(AdvertisementCreationState.description)
    except Exception as e:
        await message.bot.send_message(chat_id=config.tg_bot.main_chat_id, text="ошибка get_title_uz")
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.description)
async def get_description_set_description_uz(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:

        current_data = await state.get_data()
        description_text = current_data.pop("description_text")

        description_uz_text = await description_text.answer(
            text=get_description_text(lang="uz"),
        )

        await state.update_data(
            description=message.text,
            description_uz_text=description_uz_text,
        )
        await state.set_state(AdvertisementCreationState.description_uz)
    except Exception as e:
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_description_set_description_uz"
        )
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.description_uz)
async def get_description_uz(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        data = await state.get_data()
        description_uz_text = data.pop("description_uz_text")

        districts_text = await description_uz_text.answer(
            text="""
            Напишите номер телефона собственника
            
            пример: +998901231212
            """,
        )
        await state.update_data(
            description_uz=message.text, districts_text=districts_text
        )
        await state.set_state(AdvertisementCreationState.owner_phone_number)
    except Exception as e:
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_description_uz"
        )
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.owner_phone_number)
async def get_owner_phone_number(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        districts = await repo.districts.get_districts()

        await message.answer(
            text=get_district_text(),
            reply_markup=districts_kb(districts=districts),
        )

        await state.update_data(owner_phone_number=message.text)
        await state.set_state(AdvertisementCreationState.district)
    except Exception as e:
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_owner_phone_number"
        )
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.callback_query(
    F.data.startswith("chosen_district"),
    AdvertisementCreationState.district,
)
async def get_district_set_address(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    try:
        state_data = await state.get_data()
        current_message = state_data.pop("districts_text")

        district_id = int(call.data.split(":")[-1])
        district = await repo.districts.get_district_by_id(district_id=district_id)

        cur_message = await current_message.answer(
            text=get_address_text(district_name=district.name),
            reply_markup=None,
        )

        await state.update_data(district=district, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.address)
    except Exception as e:
        await call.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_district_set_address"
        )
        await call.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.address)
async def get_address(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        state_data = await state.get_data()
        cur_message = state_data.pop("cur_message")

        cur_message = await cur_message.answer(
            text=get_address_text_uz(),
        )

        await state.update_data(address=message.text, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.address_uz)
    except Exception as e:
        await message.bot.send_message(chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_address")
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.address_uz)
async def get_address_uz(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        state_data = await state.get_data()
        cur_message = state_data.pop("cur_message")

        cur_message = await cur_message.answer(
            text=get_propety_type_text(),
            reply_markup=property_type_kb(),
        )
        await state.update_data(address_uz=message.text, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.property_type)
    except Exception as e:
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_address_uz"
        )
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.callback_query(
    F.data.startswith("property_type"),
    AdvertisementCreationState.property_type,
)
async def get_property_type(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    try:
        state_data = await state.get_data()
        cur_message = state_data.pop("cur_message")

        _, property_type = call.data.split(":")
        property_type_name = PROPERTY_TYPE_MAPPING[property_type]

        if property_type == "new":
            cur_message = await cur_message.answer(
                text=creation_year_text(property_type=property_type_name),
            )
            await state.update_data(
                property_type=property_type, cur_message=cur_message
            )
            await state.set_state(AdvertisementCreationState.creation_year)

        if property_type == "old":
            cur_message = await cur_message.answer(
                text=price_text(property_type=property_type_name)
            )
            await state.update_data(
                property_type=property_type, cur_message=cur_message
            )
            await state.set_state(AdvertisementCreationState.price)
    except Exception as e:
        await call.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_property_type"
        )
        await call.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.creation_year)
async def get_creation_year(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        state_data = await state.get_data()
        cur_message = state_data.pop("cur_message")

        cur_message = await cur_message.answer(
            text="Напишите цену для данного объявления",
        )

        creation_year = filter_digits(message.text)

        await state.update_data(creation_year=creation_year, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.price)
    except Exception as e:
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_creation_year"
        )
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.price)
async def get_price(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        state_data = await state.get_data()
        cur_message = state_data.pop("cur_message")

        cur_message = await cur_message.answer(
            text=is_studio_text(),
            reply_markup=is_studio_kb(),
        )

        price = filter_digits(message.text)

        await state.update_data(price=price, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.is_studio)
    except Exception as e:
        await message.bot.send_message(chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_price")
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.callback_query(
    F.data.startswith("is_studio"),
    AdvertisementCreationState.is_studio,
)
async def get_is_studio(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()
    try:
        state_data = await state.get_data()

        cur_message = state_data.pop("cur_message")
        _, is_studio_state = call.data.split(":")

        is_studio = True if is_studio_state == "yes" else False

        if is_studio:
            cur_message = await cur_message.answer(
                text="Квадратура: ", reply_markup=None
            )
            await state.update_data(is_studio=is_studio, cur_message=cur_message)
            await state.set_state(AdvertisementCreationState.quadrature)
        else:
            cur_message = await cur_message.answer(
                text="Количество комнат: ", reply_markup=None
            )
            await state.update_data(is_studio=is_studio, cur_message=cur_message)
            await state.set_state(AdvertisementCreationState.rooms_quantity)
    except Exception as e:
        await call.bot.send_message(chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_is_studio")
        await call.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.rooms_quantity)
async def get_rooms_to(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        state_data = await state.get_data()
        cur_message = state_data.pop("cur_message")

        category = state_data.get("category")

        if category.slug == "doma":
            cur_message = await cur_message.answer(
                text="Площадь участка от: ",
            )
            digits = filter_digits(message.text)
            await state.update_data(rooms_quantity=digits, cur_message=cur_message)

            await state.set_state(AdvertisementCreationState.house_quadrature_from)
            return

        cur_message = await cur_message.answer(
            text="Квадратура: ",
        )

        rooms = filter_digits(message.text)
        await state.update_data(rooms_quantity=rooms, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.quadrature)
    except Exception as e:
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_rooms_to"
        )
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.house_quadrature_from)
async def get_house_quadrature_from(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        state_data = await state.get_data()
        cur_message = state_data.get("cur_message")

        cur_message = await cur_message.answer(
            text="Площадь участка до: ",
        )
        house_quadrature_from = filter_digits(message.text)
        await state.update_data(
            house_quadrature_from=house_quadrature_from,
            cur_message=cur_message,
        )
        await state.set_state(AdvertisementCreationState.house_quadrature_to)
    except Exception as e:
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_house_quadrature_from"
        )
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.house_quadrature_to)
async def get_house_quadrature_to(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        state_data = await state.get_data()
        cur_message = state_data.get("cur_message")

        cur_message = await cur_message.answer(
            text="Квадратура: ",
        )
        house_quadrature_to = filter_digits(message.text)
        await state.update_data(
            house_quadrature_to=house_quadrature_to,
            cur_message=cur_message,
        )
        await state.set_state(AdvertisementCreationState.quadrature)
    except Exception as e:
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_house_quadrature_to"
        )
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.quadrature)
async def get_quadrature(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        state_data = await state.get_data()
        cur_message = state_data.pop("cur_message")

        cur_message = await cur_message.answer(
            text="Этаж от: ",
        )

        quadrature = filter_digits(message.text)

        await state.update_data(quadrature=quadrature, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.floor_from)
    except Exception as e:
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_quadrature"
        )
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.floor_from)
async def get_floor_from(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        state_data = await state.get_data()
        cur_message = state_data.pop("cur_message")

        cur_message = await cur_message.answer(
            text="Этаж до:",
        )

        floor_from = filter_digits(message.text)

        await state.update_data(floor_from=floor_from, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.floor_to)
    except Exception as e:
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_floor_from"
        )
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.message(AdvertisementCreationState.floor_to)
async def get_floor_to(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        state_data = await state.get_data()
        cur_message = state_data.pop("cur_message")

        cur_message = await cur_message.answer(
            text="Укажите тип ремонта",
            reply_markup=repair_type_kb(REPAIR_TYPE_MAPPING),
        )

        floor_to = filter_digits(message.text)

        await state.update_data(floor_to=floor_to, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.repair_type)
    except Exception as e:
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка в get_floor_to"
        )
        await message.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )


@router.callback_query(
    F.data.startswith("repair_type"),
    AdvertisementCreationState.repair_type,
)
async def get_repair_type(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    try:
        unique_id = generate_code()
        _, repair_type = call.data.split(":")
        state_data = await state.get_data()

        operation_type = state_data.get("operation_type")
        category = state_data.get("category")
        district = state_data.get("district")

        title = state_data.get("title")
        title_uz = state_data.get("title_uz")

        description = state_data.get("description")
        description_uz = state_data.get("description_uz")

        address = state_data.get("address")
        address_uz = state_data.get("address_uz")

        property_type = state_data.get("property_type")
        creation_year = state_data.get("creation_year", 0)
        price = state_data.get("price")
        is_studio = state_data.get("is_studio")

        rooms_quantity = state_data.get("rooms_quantity")

        quadrature = state_data.get("quadrature")

        floor_from = state_data.get("floor_from")
        floor_to = state_data.get("floor_to")
        house_quadrature_from = state_data.get("house_quadrature_from", 0)
        house_quadrature_to = state_data.get("house_quadrature_to", 0)

        user_chat_id = call.message.chat.id
        user = await repo.users.get_user_by_chat_id(user_chat_id)

        operation_type_status = OperationType(OPERATION_TYPE_MAPPING[operation_type])
        operation_type_status_uz = OperationTypeUz(
            OPERATION_TYPE_MAPPING_UZ[operation_type]
        )
        property_type_status = PropertyType(PROPERTY_TYPE_MAPPING[property_type])
        property_type_status_uz = PropertyTypeUz(
            PROPERTY_TYPE_MAPPING_UZ[property_type]
        )
        repair_type_status = RepairType(REPAIR_TYPE_MAPPING[repair_type])
        repair_type_status_uz = RepairTypeUz(REPAIR_TYPE_MAPPING_UZ[repair_type])

        photos = state_data.get("photos")
        date_str = datetime.now().strftime("%Y-%m-%d")
        owner_phone_number = state_data.get("owner_phone_number")

        advertisements_folder = upload_dir / "advertisements" / date_str
        advertisements_folder.mkdir(parents=True, exist_ok=True)
        files_locations = []

        # preview
        preview_file_id = state_data.get("preview_file_id")
        preview_file_obj = await call.bot.get_file(preview_file_id)
        preview_filename = preview_file_obj.file_path.split("/")[-1]
        preview_file = await call.bot.download_file(preview_file_obj.file_path)
        preview_file_location = advertisements_folder / preview_filename
        with open(preview_file_location, "wb") as f:
            shutil.copyfileobj(preview_file, f)

        # other photos
        for photo_id in photos:
            file_obj = await call.bot.get_file(photo_id)
            filename = file_obj.file_path.split("/")[-1]
            file = await call.bot.download_file(file_obj.file_path)

            file_location = advertisements_folder / filename
            files_locations.append((file_location, photo_id))

            with open(file_location, "wb") as f:
                shutil.copyfileobj(file, f)

        new_advertisement = await repo.advertisements.create_advertisement(
            unique_id=unique_id,
            operation_type=operation_type_status,
            category=category.id,
            district=district.id,
            title=title,
            title_uz=title_uz,
            description=description,
            description_uz=description_uz,
            preview=str(preview_file_location),
            address=address,
            address_uz=address_uz,
            property_type=property_type_status,
            creation_year=int(creation_year),
            price=int(price),
            is_studio=is_studio,
            rooms_quantity=int(rooms_quantity) if rooms_quantity is not None else 0,
            quadrature=int(quadrature),
            floor_from=int(floor_from),
            floor_to=int(floor_to),
            house_quadrature_from=int(house_quadrature_from),
            house_quadrature_to=int(house_quadrature_to),
            repair_type=repair_type_status,
            operation_type_uz=operation_type_status_uz,
            property_type_uz=property_type_status_uz,
            repair_type_uz=repair_type_status_uz,
            user=user.id,
            owner_phone_number=owner_phone_number,
        )

        advertisement_message = realtor_advertisement_completed_text(
            new_advertisement, lang="uz"
        )

        for file_location, photo_id in files_locations:
            await repo.advertisement_images.insert_advertisement_image(
                advertisement_id=new_advertisement.id,
                url=str(file_location),
                tg_image_hash=photo_id,
            )

        media_group = get_media_group(photos, advertisement_message)

        group_directors = await repo.users.get_users_by_role(role="GROUP_DIRECTOR")

        await call.message.answer_media_group(media=media_group)

        for director in group_directors:
            try:
                if (
                        director.tg_chat_id
                        and director.tg_chat_id == new_advertisement.user.added_by
                ):
                    realtor_fullname = f"{new_advertisement.user.first_name} {new_advertisement.user.lastname}"
                    await call.bot.send_message(
                        director.tg_chat_id,
                        f"Риелтор: {realtor_fullname} добавил новое объявление",
                    )
                    await call.bot.send_media_group(
                        director.tg_chat_id, media=media_group
                    )
                    await call.bot.send_message(
                        director.tg_chat_id,
                        f"Объявление прошло модерацию?",
                        reply_markup=advertisement_moderation_kb(new_advertisement.id),
                    )
            except Exception as e:
                logger.error(e)
                await call.bot.send_message(
                    chat_id=config.tg_bot.main_chat_id, text=f"ошибка при отправке руководителям"
                )
                await call.bot.send_message(
                    chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
                )

        await call.message.answer(
            text="Выберите действие над этим объявлением",
            reply_markup=advertisement_actions_kb(
                advertisement_id=new_advertisement.id
            ),
        )
    except Exception as e:
        logger.error(e)
        await call.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"ошибка при создании объявления"
        )
        await call.bot.send_message(
            chat_id=config.tg_bot.main_chat_id, text=f"{e}\n{e.__class__.__name__}"
        )
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')