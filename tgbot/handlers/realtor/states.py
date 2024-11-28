import shutil
from datetime import datetime
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto

from backend.core.interfaces.category import CategoryDTO
from infrastructure.database.models.advertisement import (
    OperationType,
    PropertyType,
    RepairType,
)
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.keyboards.user.inline import (
    categories_kb,
    districts_kb,
    is_studio_kb,
    property_type_kb,
    repair_type_kb,
)
from tgbot.misc.user_states import AdvertisementCreationState
from tgbot.templates.advertisement_creation import (
    choose_category_text,
    choose_photos_quantity_text,
    choose_photos_text,
    creation_year_text,
    get_address_text,
    get_description_text,
    get_district_text,
    get_propety_type_text,
    get_title_text,
    is_studio_text,
    price_text,
    realtor_advertisement_completed_text,
)

router = Router()

OPERATION_TYPE_MAPPING = {
    "rent": "Аренда",
    "buy": "Покупка",
}
PROPERTY_TYPE_MAPPING = {
    "new": "Новостройка",
    "old": "Вторичный фонд",
}


REPAIR_TYPE_MAPPING = {
    "with": "С ремонтом",
    "without": "Без ремонта",
    "designed": "Дизайнерский ремонт",
    "rough": "Черновая",
    "pre_finished": "Предчистовая",
}

upload_dir = Path("media")
upload_dir.mkdir(parents=True, exist_ok=True)


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

    await call.message.edit_text(
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

    message = await call.message.edit_text(
        text=choose_photos_quantity_text(category_name=category.name),
    )

    await state.update_data(category=category, photos_qty_message=message)
    await state.set_state(AdvertisementCreationState.photos_quantity)


@router.message(AdvertisementCreationState.photos_quantity)
async def get_photos_quanity_set_get_photos(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()

    photos_qty_message = state_data.pop("photos_qty_message")

    # await message.delete()

    photos_message = await photos_qty_message.edit_text(
        text=choose_photos_text(photos_quantity=message.text)
    )
    await message.delete()

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
    current_message = current_state.pop("photos_message")
    current_state["photos"].append(message.photo[-1].file_id)

    try:
        await message.delete()
    except Exception as e:
        pass

    if current_state["photos_quantity"] == len(current_state["photos"]):
        await current_message.delete()

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

    description_text = await title_message.edit_text(text=get_description_text())

    await state.update_data(title=message.text, description_text=description_text)
    await state.set_state(AdvertisementCreationState.description)
    await message.delete()


@router.message(AdvertisementCreationState.description)
async def get_description_set_disctrict(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    current_data = await state.get_data()
    description_text = current_data.pop("description_text")

    districts = await repo.districts.get_districts()

    districts_text = await description_text.edit_text(
        text=get_district_text(),
        reply_markup=districts_kb(districts=districts),
    )

    await state.update_data(description=message.text, districts_text=districts_text)
    await state.set_state(AdvertisementCreationState.district)
    await message.delete()


@router.callback_query(
    F.data.startswith("chosen_district"), AdvertisementCreationState.district
)
async def get_district_set_address(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    state_data = await state.get_data()
    current_message = state_data.pop("districts_text")

    district_id = int(call.data.split(":")[-1])
    district = await repo.districts.get_district_by_id(district_id=district_id)

    cur_message = await current_message.edit_text(
        text=get_address_text(district_name=district.name),
        reply_markup=None,
    )

    await state.update_data(district=district, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.address)


@router.message(AdvertisementCreationState.address)
async def get_address(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    cur_message = state_data.pop("cur_message")

    cur_message = await cur_message.edit_text(
        text=get_propety_type_text(),
        reply_markup=property_type_kb(),
    )

    await state.update_data(address=message.text, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.property_type)
    await message.delete()


@router.callback_query(
    F.data.startswith("property_type"), AdvertisementCreationState.property_type
)
async def get_property_type(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    state_data = await state.get_data()
    cur_message = state_data.pop("cur_message")

    _, property_type = call.data.split(":")
    property_type_name = PROPERTY_TYPE_MAPPING[property_type]

    if property_type == "new":
        cur_message = await cur_message.edit_text(
            text=creation_year_text(property_type=property_type_name),
        )
        await state.update_data(property_type=property_type, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.creation_year)

    if property_type == "old":
        cur_message = await cur_message.edit_text(
            text=price_text(property_type=property_type_name)
        )
        await state.update_data(property_type=property_type, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.price)


@router.message(AdvertisementCreationState.creation_year)
async def get_creation_year(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    cur_message = state_data.pop("cur_message")

    cur_message = await cur_message.edit_text(
        text="Напишите цену для данного объявления",
    )

    await state.update_data(creation_year=message.text, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.price)
    await message.delete()


@router.message(AdvertisementCreationState.price)
async def get_price(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    cur_message = state_data.pop("cur_message")

    cur_message = await cur_message.edit_text(
        text=is_studio_text(),
        reply_markup=is_studio_kb(),
    )

    await state.update_data(price=message.text, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.is_studio)
    await message.delete()


@router.callback_query(
    F.data.startswith("is_studio"),
    AdvertisementCreationState.is_studio,
)
async def is_studio(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    state_data = await state.get_data()

    cur_message = state_data.pop("cur_message")
    _, is_studio_state = call.data.split(":")

    is_studio = True if is_studio_state == "yes" else False

    if is_studio:
        cur_message = await cur_message.edit_text(
            text="Квадратура от: ", reply_markup=None
        )
        await state.update_data(is_studio=is_studio, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.quadrature_from)
    else:
        cur_message = await cur_message.edit_text(
            text="Количество комнат от: ", reply_markup=None
        )
        await state.update_data(is_studio=is_studio, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.rooms_from)


@router.message(AdvertisementCreationState.rooms_from)
async def get_rooms_from(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    cur_message = state_data.pop("cur_message")

    cur_message = await cur_message.edit_text(
        text="Количество комнат до:",
    )
    await state.update_data(rooms_from=message.text, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.rooms_to)
    await message.delete()


@router.message(AdvertisementCreationState.rooms_to)
async def get_rooms_to(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    cur_message = state_data.pop("cur_message")

    category = state_data.get("category")

    if category.slug == "doma":
        cur_message = await cur_message.edit_text(
            text="Площадь участка от: ",
        )
        await state.update_data(rooms_to=message.text, cur_message=cur_message)
        await state.set_state(AdvertisementCreationState.house_quadrature_from)
        return await message.delete()

    cur_message = await cur_message.edit_text(
        text="Квадратура от: ",
    )
    await state.update_data(rooms_to=message.text, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.quadrature_from)
    await message.delete()


@router.message(AdvertisementCreationState.house_quadrature_from)
async def get_house_quadrature_from(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    cur_message = state_data.get("cur_message")

    cur_message = await cur_message.edit_text(
        text="Площадь участка до: ",
    )
    await state.update_data(house_quadrature_from=message.text, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.house_quadrature_to)
    await message.delete()


@router.message(AdvertisementCreationState.house_quadrature_to)
async def get_house_quadrature_to(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    cur_message = state_data.get("cur_message")

    cur_message = await cur_message.edit_text(
        text="Квадратура от: ",
    )
    await state.update_data(house_quadrature_to=message.text, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.quadrature_from)
    await message.delete()


@router.message(AdvertisementCreationState.quadrature_from)
async def get_quadrature_from(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    cur_message = state_data.pop("cur_message")

    cur_message = await cur_message.edit_text(
        text="Квадратура до: ",
    )

    await state.update_data(quadrature_from=message.text, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.quadrature_to)
    await message.delete()


@router.message(AdvertisementCreationState.quadrature_to)
async def get_quadrature_to(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):

    state_data = await state.get_data()
    cur_message = state_data.pop("cur_message")

    cur_message = await cur_message.edit_text(
        text="Этаж от: ",
    )

    await state.update_data(quadrature_to=message.text, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.floor_from)
    await message.delete()


@router.message(AdvertisementCreationState.floor_from)
async def get_floor_from(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    cur_message = state_data.pop("cur_message")

    cur_message = await cur_message.edit_text(
        text="Этаж до:",
    )
    await state.update_data(floor_from=message.text, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.floor_to)
    await message.delete()


@router.message(AdvertisementCreationState.floor_to)
async def get_floor_to(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    cur_message = state_data.pop("cur_message")

    cur_message = await cur_message.edit_text(
        text="Укажите тип ремонта",
        reply_markup=repair_type_kb(REPAIR_TYPE_MAPPING),
    )
    await state.update_data(floor_to=message.text, cur_message=cur_message)
    await state.set_state(AdvertisementCreationState.repair_type)
    await message.delete()


@router.callback_query(F.data.startswith("repair_type"))
async def get_repair_type(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    print("STARTED")
    _, repair_type = call.data.split(":")
    state_data = await state.get_data()
    cur_message = state_data.pop("cur_message")

    operation_type = state_data.get("operation_type")
    category = state_data.get("category")
    district = state_data.get("district")

    title = state_data.get("title")
    description = state_data.get("description")
    address = state_data.get("address")
    property_type = state_data.get("property_type")
    creation_year = state_data.get("creation_year", 0)
    price = state_data.get("price")
    is_studio = state_data.get("is_studio")
    rooms_from = state_data.get("rooms_from", 0)
    rooms_to = state_data.get("rooms_to", 0)
    quadrature_from = state_data.get("quadrature_from")
    quadrature_to = state_data.get("quadrature_to")
    floor_from = state_data.get("floor_from")
    floor_to = state_data.get("floor_to")
    house_quadrature_from = state_data.get("house_quadrature_from", 0)
    house_quadrature_to = state_data.get("house_quadrature_to", 0)

    user_chat_id = call.message.chat.id
    user = await repo.users.get_user_by_chat_id(user_chat_id)

    operation_type_status = OperationType(OPERATION_TYPE_MAPPING[operation_type])
    property_type_status = PropertyType(PROPERTY_TYPE_MAPPING[property_type])
    repair_type_status = RepairType(REPAIR_TYPE_MAPPING[repair_type])

    new_advertisement = await repo.advertisements.create_advertisement(
        operation_type=operation_type_status,
        category=category.id,
        district=district.id,
        title=title,
        description=description,
        address=address,
        property_type=property_type_status,
        creation_year=int(creation_year),
        price=int(price),
        is_studio=is_studio,
        rooms_from=int(rooms_from),
        rooms_to=int(rooms_to),
        quadrature_from=int(quadrature_from),
        quadrature_to=int(quadrature_to),
        floor_from=int(floor_from),
        floor_to=int(floor_to),
        house_quadrature_from=int(house_quadrature_from),
        house_quadrature_to=int(house_quadrature_to),
        repair_type=repair_type_status,
        user=user.id,
    )

    photos = state_data.get("photos")
    date_str = datetime.now().strftime("%Y-%m-%d")

    advertisements_folder = upload_dir / "advertismenets" / date_str
    advertisements_folder.mkdir(parents=True, exist_ok=True)

    files_locations = []

    # for photo_id in photos:
    #     file_obj = await call.bot.get_file(photo_id)
    #     filename = file_obj.file_path.split("/")[-1]
    #     file = await call.bot.download_file(file_obj.file_path)

    #     file_location = advertisements_folder / filename
    #     files_locations.append(file_location)

    #     await repo.advertisement_images.insert_advertisement_image(
    #         advertisement_id=new_advertisement.id,
    #         url=file_location,
    #     )

    #     with open(file_location, "wb") as f:
    #         shutil.copyfileobj(file, f)

    # media_group = []
    # for idx, location in enumerate(files_locations):
    #     if idx == 0:
    #         media_group.append(
    #             InputMediaPhoto(
    #                 open(location, "rb"),
    #                 caption=advertisement_message,
    #             )
    #         )
    #     else:
    #         media_group.append(InputMediaPhoto(open(location, "rb")))

    advertisement_message = realtor_advertisement_completed_text(
        title=title,
        description=description,
        address=address,
        property_type=property_type,
        creation_year=creation_year,
        price=price,
        is_studio=is_studio,
        rooms_from=rooms_from,
        rooms_to=rooms_to,
        quadrature_from=quadrature_from,
        quadrature_to=quadrature_to,
        floor_from=floor_from,
        floor_to=floor_to,
        house_quadrature_from=house_quadrature_from,
        house_quadrature_to=house_quadrature_to,
        repair_type=repair_type,
        operation_type=operation_type,
        category=category,
        district=district,
    )
    await call.message.answer(advertisement_message)

    # await call.message.answer_media_group(media=media_group)
