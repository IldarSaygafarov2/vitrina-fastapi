from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters.command import Command

from backend.app.config import config
from backend.core.interfaces.advertisement import AdvertisementForReportDTO
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.misc.constants import ROW_FIELDS, MONTHS_DICT
from tgbot.utils.google_sheet import client_init_json, get_table_by_url, update_row_values

router = Router()


@router.message(Command('get_report'), F.chat.id == config.tg_bot.test_main_chat_id)
async def get_month_report(message: types.Message, repo: "RequestsRepo"):
    chat_id = message.chat.id

    month = datetime.now().month - 1

    advertisements = await repo.advertisements.get_advertisements_by_month(month)
    _advertisements = []

    client = client_init_json()
    spreadsheet = get_table_by_url(client, config.report_sheet.report_sheet_link)


    for item in advertisements:
        item = AdvertisementForReportDTO.model_validate(item, from_attributes=True).model_dump()
        item['created_at'] = item['created_at'].strftime("%d.%m.%Y %H:%M:%S")
        item['category'] = item['category']['name']
        item['district'] = item['district']['name']
        item['user'] = item['user']['fullname'] if item.get('user') else ''
        _advertisements.append(item)

    update_row_values(spreadsheet, worksheet_name=MONTHS_DICT[month], values=_advertisements)
