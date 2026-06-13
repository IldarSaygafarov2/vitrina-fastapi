import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Annotated

import requests
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.app.dependencies import get_repo
from backend.core.interfaces.advertisement import AdvertisementHtmlDTO
from config.constants import (
    OPERATION_TYPE_MAPPING,
    OPERATION_TYPE_MAPPING_UZ,
    PROPERTY_TYPE_MAPPING,
    PROPERTY_TYPE_MAPPING_UZ,
    REPAIR_TYPE_MAPPING,
    REPAIR_TYPE_MAPPING_UZ,
)
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
from infrastructure.utils.helpers import get_unique_code
from tgbot.templates.advertisement_creation import realtor_advertisement_completed_text
from tgbot.utils.helpers import (
    get_media_group,
    prepare_media_group_for_request,
    prepare_moderation_kb,
)
from backend.api.websockets.manager import manager

config = load_config()

router = APIRouter()

upload_dir = Path("media")
upload_dir.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory="backend/templates")

MEDIA_GROUP_URL = f"https://api.telegram.org/bot{config.tg_bot.token}/sendMediaGroup"
SEND_MESSAGE_URL = f"https://api.telegram.org/bot{config.tg_bot.token}/sendMessage"


@router.get("/", response_class=HTMLResponse)
async def show_home_page(
    request: Request, repo: Annotated[RequestsRepo, Depends(get_repo)]
):
    # await manager.send_personal_message("test", 1)
    categories = await repo.categories.get_categories()
    districts = await repo.districts.get_districts()

    # await manager.connect()

    return templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request,
            "title": "home page",
            "categories": categories,
            "districts": districts,
            "repair_types": REPAIR_TYPE_MAPPING,
        },
    )


@router.post("/submit-form/")
async def submit_form(
    request: Request,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
    user_id: Annotated[str, Form()],
    operation_type: Annotated[str, Form()],
    category: Annotated[str, Form()],
    title_ru: Annotated[str, Form()],
    title_uz: Annotated[str, Form()],
    description_ru: Annotated[str, Form()],
    description_uz: Annotated[str, Form()],
    owner_phone_number: Annotated[str, Form()],
    district: Annotated[str, Form()],
    address_ru: Annotated[str, Form()],
    address_uz: Annotated[str, Form()],
    property_type: Annotated[str, Form()],
    creation_year: Annotated[str, Form()],
    price: Annotated[str, Form()],
    rooms_quantity: Annotated[str, Form()],
    house_quadrature: Annotated[str, Form()],
    quadrature: Annotated[str, Form()],
    floors: Annotated[str, Form()],
    floor_number: Annotated[str, Form()],
    repair_type: Annotated[str, Form()],
    photos: list[UploadFile] = File(...),
):
    # agent and agent director data
    current_user = await repo.users.get_user_by_id(user_id=int(user_id))
    agent_director = await repo.users.get_user_by_chat_id(
        tg_chat_id=current_user.added_by
    )
    agent_fullname = f"{current_user.first_name} {current_user.lastname}"

    # form data
    category_id = int(category.split("-")[-1])
    district_id = int(district.split("-")[-1])

    unique_code = await get_unique_code(repo)

    operation_type_status = OperationType(OPERATION_TYPE_MAPPING[operation_type])
    operation_type_status_uz = OperationTypeUz(
        OPERATION_TYPE_MAPPING_UZ[operation_type]
    )
    property_type_status = PropertyType(PROPERTY_TYPE_MAPPING[property_type])
    property_type_status_uz = PropertyTypeUz(PROPERTY_TYPE_MAPPING_UZ[property_type])
    repair_type_status = RepairType(REPAIR_TYPE_MAPPING[repair_type])
    repair_type_status_uz = RepairTypeUz(REPAIR_TYPE_MAPPING_UZ[repair_type])

    date_str = datetime.now().strftime("%Y-%m-%d")
    advertisements_folder = upload_dir / "advertisements" / date_str
    advertisements_folder.mkdir(parents=True, exist_ok=True)
    preview_file = advertisements_folder / photos[0].filename

    # saving photos
    # with open(preview_file, "wb") as buffer:
    #     shutil.copyfileobj(photos[0].file, buffer)

    # buffer.seek(0)
    photos_paths_list = []
    for photo in photos:
        photo_path = advertisements_folder / photo.filename
        with open(photo_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        photos_paths_list.append(photo_path)

    # advertisement creation
    new_advertisement = await repo.advertisements.create_advertisement(
        unique_id=unique_code,
        operation_type=operation_type_status,
        category=category_id,
        district=district_id,
        title=title_ru,
        title_uz=title_uz,
        description=description_ru,
        description_uz=description_uz,
        preview=str(photos_paths_list[0]),
        address=address_ru,
        address_uz=address_uz,
        property_type=property_type_status,
        creation_year=int(creation_year) if creation_year else 0,
        price=int(price),
        rooms_quantity=int(rooms_quantity) if rooms_quantity is not None else 0,
        quadrature=int(quadrature),
        floor_from=int(floors),
        floor_to=int(floor_number),
        house_quadrature_from=int(house_quadrature),
        house_quadrature_to=int(house_quadrature),
        repair_type=repair_type_status,
        operation_type_uz=operation_type_status_uz,
        property_type_uz=property_type_status_uz,
        repair_type_uz=repair_type_status_uz,
        user=int(user_id),
        owner_phone_number=owner_phone_number,
        reminder_time=None,
    )
    new_advertisement = await repo.advertisements.update_advertisement(
        advertisement_id=new_advertisement.id, old_price=int(price)
    )

    # saving photos to db
    for file_location in photos_paths_list:
        await repo.advertisement_images.insert_advertisement_image(
            advertisement_id=new_advertisement.id,
            url=str(file_location),
        )

    # sending media group and messages to director in telegram bot

    message_for_director = f"Риелтор: {agent_fullname} добавил новое объявление"

    requests.post(
        SEND_MESSAGE_URL,
        data={"chat_id": agent_director.tg_chat_id, "text": message_for_director},
    )

    new_advertisement_url = (
        f"http://127.0.0.1:8888/new-advertisement/{new_advertisement.id}"
    )
    requests.post(
        SEND_MESSAGE_URL,
        data={
            "chat_id": agent_director.tg_chat_id,
            "text": f"""Агент: {current_user.fullname} добавил новое объявление.
Чтобы посмотреть объявление перейдите по ссылке
<a href='{new_advertisement_url}'>перейти</a>""",
            "parse_mode": "HTML",
        },
    )

    return RedirectResponse(url="/", status_code=status.HTTP_301_MOVED_PERMANENTLY)


@router.get("/new-advertisement/{advertisement_id}", response_class=HTMLResponse)
async def new_advertisement_page(
    request: Request,
    advertisement_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    if not advertisement:
        return templates.TemplateResponse("pages/404.html", {"request": request})
    advertisement_data = AdvertisementHtmlDTO.model_validate(
        advertisement, from_attributes=True
    ).model_dump()

    text = realtor_advertisement_completed_text(advertisement, lang="uz", for_html=True)

    text = "<br/>".join(text.split("="))

    return templates.TemplateResponse(
        "pages/new_advertisement.html",
        {"request": request, "advertisement": advertisement_data, "text": text},
    )
