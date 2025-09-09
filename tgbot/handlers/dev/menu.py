from aiogram import types, Router, F
from aiogram.filters import CommandStart

from infrastructure.database.repo.requests import RequestsRepo

from backend.app.config import config
from tgbot.utils.google_sheet import client_init_json, get_table_by_url, get_sheet_values
from tgbot.misc.constants import MONTHS_DICT, ROW_FIELDS

dev_router = Router()


# @dev_router.message(F.from_user.id == config.tg_bot.test_main_chat_id, CommandStart())
# async def dev_start(message: types.Message, repo: RequestsRepo):
#     current_month = message.date.month
#
#     row_fields_keys = list(ROW_FIELDS.keys())
#
#     client = client_init_json()
#     rent_spread = get_table_by_url(client, url=config.report_sheet.rent_report_sheet_link)
#     buy_spread = get_table_by_url(client, url=config.report_sheet.buy_report_sheet_link)
#
#     buy_spread_values = get_sheet_values(buy_spread, worksheet_name=MONTHS_DICT[current_month])
#     buy_spread_values = [dict(zip(row_fields_keys, item)) for item in buy_spread_values]
#
#     for item in buy_spread_values:
#         if not item['user_id']:
#             unique_id = item['unique_id']
#             adv = await repo.advertisements.get_advertisement_by_unique_id(unique_id=unique_id)
#             print(f'{adv=}', unique_id)
