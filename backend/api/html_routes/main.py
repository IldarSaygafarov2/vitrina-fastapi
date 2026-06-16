import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Annotated

import requests
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.api.html_routes import utils as html_utils
from backend.app.dependencies import get_repo
from backend.core.interfaces.advertisement import AdvertisementHtmlDTO
from celery_tasks.tasks import fill_agent_report, fill_report
from config.constants import (
    OPERATION_TYPE_MAPPING,
    OPERATION_TYPE_RU_UZ,
    PROPERTY_TYPE_MAPPING,
    PROPERTY_TYPE_RU_UZ,
    REPAIR_TYPE_MAPPING,
    REPAIR_TYPE_MAPPING_UZ,
    SEND_MESSAGE_URL,
    MEDIA_GROUP_URL,
    REPAIR_TYPE_RU_UZ,
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
from infrastructure.utils.helpers import generate_item_for_sheet_table, get_unique_code
from tgbot.templates.advertisement_creation import realtor_advertisement_completed_text
from tgbot.utils.helpers import (
    get_channel_name_and_message_by_operation_type,
    prepart_data_for_report,
)
from celery_tasks.tasks import send_media_to_telegram
from .forms import AdvertisementForm

config = load_config()

router = APIRouter()

upload_dir = Path("media")
upload_dir.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory="backend/templates")


def prepare_form_data(form: AdvertisementForm):
    form.category_id = int(form.category_id)
    form.district_id = int(form.district_id)
    form.price = int(form.price)
    form.rooms_quantity = int(form.rooms_quantity)
    form.house_quadrature_from = (
        int(form.house_quadrature_from) if form.house_quadrature_from else 0
    )
    form.quadrature = int(form.quadrature)
    form.user_id = int(form.user_id)
    form.creation_year = int(form.creation_year) if form.creation_year else 0

    form.property_type = PropertyType[form.property_type.upper()]
    form.operation_type = OperationType[form.operation_type.upper()]
    form.repair_type = RepairType[form.repair_type.upper()]
    return form


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
    photos: list[UploadFile] = File(...),
):
    # parse form data (multipart/form-data) into AdvertisementForm
    form_data = await request.form()
    form_data_dict = {**dict(form_data)}
    form = AdvertisementForm(**dict(form_data))

    form = prepare_form_data(form)

    # agent and agent director data
    current_user = await repo.users.get_user_by_id(user_id=int(form.user_id))
    agent_director = await repo.users.get_user_by_chat_id(
        tg_chat_id=current_user.added_by
    )

    # form data
    unique_code = await get_unique_code(repo)

    operation_type_status = OperationType(
        OPERATION_TYPE_MAPPING[form_data_dict.get("operation_type")]
    )
    operation_type_status_uz = OperationTypeUz(
        OPERATION_TYPE_RU_UZ[operation_type_status.value]
    )
    # PROPERTY_TYPE
    property_type_status = PropertyType(
        PROPERTY_TYPE_MAPPING[form_data_dict.get("property_type")]
    )
    print("property_type_status".upper(), property_type_status)
    property_type_status_uz = PropertyTypeUz(
        PROPERTY_TYPE_RU_UZ[property_type_status.value]
    )
    print("property_type_status_uz".upper(), property_type_status_uz)
    repair_type_status = RepairType(
        REPAIR_TYPE_MAPPING[form_data_dict.get("repair_type")]
    )
    repair_type_status_uz = RepairTypeUz(REPAIR_TYPE_RU_UZ[repair_type_status.value])

    date_str = datetime.now().strftime("%Y-%m-%d")
    advertisements_folder = upload_dir / "advertisements" / date_str
    advertisements_folder.mkdir(parents=True, exist_ok=True)

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
        category=form.category_id,
        district=form.district_id,
        title=form.name,
        title_uz=form.name_uz,
        description=form.description,
        description_uz=form.description_uz,
        preview=str(photos_paths_list[0]),
        address=form.address,
        address_uz=form.address_uz,
        property_type=property_type_status,
        creation_year=int(form.creation_year) if form.creation_year else 0,
        price=int(form.price),
        rooms_quantity=(
            int(form.rooms_quantity) if form.rooms_quantity is not None else 0
        ),
        quadrature=int(form.quadrature),
        floor_from=int(form.floor_from),
        floor_to=int(form.floor_to),
        house_quadrature_from=int(form.house_quadrature_from),
        house_quadrature_to=int(form.house_quadrature_from),
        repair_type=repair_type_status,
        operation_type_uz=operation_type_status_uz,
        property_type_uz=property_type_status_uz,
        repair_type_uz=repair_type_status_uz,
        user=int(form.user_id),
        owner_phone_number=form.owner_phone_number,
        reminder_time=None,
    )
    new_advertisement = await repo.advertisements.update_advertisement(
        advertisement_id=new_advertisement.id, old_price=int(form.price)
    )

    # saving photos to db
    for file_location in photos_paths_list:
        await repo.advertisement_images.insert_advertisement_image(
            advertisement_id=new_advertisement.id,
            url=str(file_location),
        )

    new_advertisement_url = (
        f"{request.base_url}new-advertisement/{new_advertisement.id}"
    )
    requests.post(
        SEND_MESSAGE_URL.format(BOT_TOKEN=config.tg_bot.token),
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


@router.get(
    "/new-advertisement/{advertisement_id}/moderation/",
    response_class=HTMLResponse,
)
async def moderate_new_advertisement(
    request: Request,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
    advertisement_id: int,
    is_moderated: bool = False,
):
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    if not advertisement:
        return templates.TemplateResponse("pages/404.html", {"request": request})

    operation_type = advertisement.operation_type.value

    context = {
        "request": request,
        "advertisement": advertisement,
        "is_moderated": is_moderated,
    }

    # agent_advertisement_data = generate_item_for_sheet_table(advertisement)
    advertisement_data = prepart_data_for_report(advertisement)
    month = datetime.now().month

    fill_report.delay(
        month=month,
        operation_type=operation_type,
        data=advertisement_data,
    )

    # user = await repo.users.get_user_by_id(advertisement.user_id)

    # sheet_link = (
    #     user.spreadsheet_rent_url
    #     if operation_type == "Аренда"
    #     else user.spreadsheet_buy_url
    # )

    # fill_agent_report.delay(
    #     month=month,
    #     data=agent_advertisement_data,
    #     sheet_link=sheet_link,
    # )

    if is_moderated:
        advertisement = await repo.advertisements.update_advertisement(
            advertisement_id=advertisement_id, is_moderated=True
        )
        channel_name, advertisement_message = (
            get_channel_name_and_message_by_operation_type(advertisement)
        )

        images = [i.url for i in advertisement.images]
        media, files, photos_paths = html_utils.prepare_media_group_for_request(
            images, advertisement_message
        )

        html_utils.send_message_to_rent_topic(
            advertisement.price,
            operation_type,
            media_group=media,
            files=files,
        )

        send_media_to_telegram.delay(
            {"chat_id": channel_name, "media": json.dumps(media)},
            photos_paths,
        )

        if advertisement.operation_type.value == "Покупка":
            send_media_to_telegram.delay(
                {
                    "chat_id": config.tg_bot.base_channel_name,
                    "media": json.dumps(media),
                },
                photos_paths,
            )

        return templates.TemplateResponse("pages/moderation_confirm.html", context)
    return templates.TemplateResponse("pages/advertisement_moderation.html", context)


@router.post(
    "/new-advertisement/{advertisement_id}/moderation/deny/",
    response_class=HTMLResponse,
)
async def deny_advertisement(
    request: Request,
    advertisement_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
    form_message: Annotated[str, Form()],
):
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    if not advertisement:
        return templates.TemplateResponse("pages/404.html", {"request": request})

    await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id, is_moderated=False
    )

    agent = advertisement.user
    new_advertisement_url = f"{request.base_url}/new-advertisement/{advertisement_id}"

    requests.post(
        SEND_MESSAGE_URL.format(BOT_TOKEN=config.tg_bot.token),
        data={
            "chat_id": agent.tg_chat_id,
            "text": f"""Объявление не прошло модерацию
Причина: <b>{form_message}</b>

<a href='{new_advertisement_url}'>перейти</a>""",
            "parse_mode": "HTML",
        },
    )
    return RedirectResponse(
        f"/new-advertisement/{advertisement_id}/",
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
    )


@router.get("/new-advertisement/{advertisement_id}/edit/", response_class=HTMLResponse)
async def edit_advertisement_page(
    request: Request,
    advertisement_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):

    context = {
        "request": request,
        "categories": await repo.categories.get_categories(),
        "districts": await repo.districts.get_districts(),
        "repair_types": REPAIR_TYPE_MAPPING,
    }
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    print(advertisement.name)
    if not advertisement_id:
        return templates.TemplateResponse("pages/404.html", context)
    context.update({"advertisement": advertisement})
    return templates.TemplateResponse("pages/advertisement_edit.html", context)


@router.post("/edit-advertisement/{advertisement_id}/", response_class=HTMLResponse)
async def edit_advertisement_from_form(
    request: Request,
    advertisement_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
    photos: list[UploadFile] = File(...),
):
    form_data = await request.form()
    form = AdvertisementForm(**dict(form_data))

    form = prepare_form_data(form)

    # advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    # if not advertisement:
    #     return templates.TemplateResponse("pages/404.html", context)

    updated = await repo.advertisements.update_advertisement(
        advertisement_id, **form.model_dump()
    )

    context = {
        "request": request,
        "categories": await repo.categories.get_categories(),
        "districts": await repo.districts.get_districts(),
        "repair_types": REPAIR_TYPE_MAPPING,
        "advertisement": updated,
    }
    return templates.TemplateResponse("pages/advertisement_edit.html", context)
