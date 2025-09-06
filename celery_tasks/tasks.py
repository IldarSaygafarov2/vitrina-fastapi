import time

from backend.core.interfaces.advertisement import AdvertisementForReportDTO
from celery_tasks.app import celery_app

from tgbot.misc.constants import MONTHS_DICT
from tgbot.utils.google_sheet import client_init_json, get_table_by_url, update_row_values, fill_row_with_data
from backend.app.config import config


@celery_app.task
def add(x, y):
    print(f"Adding {x} + {y} = {x + y}")



@celery_app.task
def fill_report(month: int, data: dict, operation_type: str):
    client = client_init_json()

    spread = None
    if operation_type == 'Аренда':
        spread = get_table_by_url(client, config.report_sheet.rent_report_sheet_link)
    elif operation_type == 'Покупка':
        spread = get_table_by_url(client, config.report_sheet.buy_report_sheet_link)

    fill_row_with_data(spread, worksheet_name=MONTHS_DICT[month], data=data)
    time.sleep(2)



@celery_app.task
def fill_advertisements_report(month: int, advertisements: list[AdvertisementForReportDTO]):
    _advertisements_rent = []
    _advertisements_buy = []

    client = client_init_json()
    rent_spreadsheet = get_table_by_url(client, config.report_sheet.rent_report_sheet_link)
    buy_spreadsheet = get_table_by_url(client, config.report_sheet.buy_report_sheet_link)

    for item in advertisements:
        # item = AdvertisementForReportDTO.model_validate(item, from_attributes=True).model_dump()
        item['created_at'] = item['created_at'].strftime("%d.%m.%Y %H:%M:%S")
        item['category'] = item['category']['name']
        item['district'] = item['district']['name']
        item['user'] = item['user']['fullname'] if item.get('user') else ''
        if item['operation_type'] == 'Аренда':
            _advertisements_rent.append(item)
        elif item['operation_type'] == 'Покупка':
            _advertisements_buy.append(item)

    update_row_values(rent_spreadsheet, worksheet_name=MONTHS_DICT[month], values=_advertisements_rent)
    update_row_values(buy_spreadsheet, worksheet_name=MONTHS_DICT[month], values=_advertisements_buy)
