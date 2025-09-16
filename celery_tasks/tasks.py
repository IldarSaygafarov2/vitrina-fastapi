import time

from backend.app.config import config
from celery_tasks.app import celery_app
from tgbot.misc.constants import MONTHS_DICT
from tgbot.utils.google_sheet import (
    client_init_json,
    get_table_by_url,
    fill_row_with_data,
)


@celery_app.task
def fill_report(month: int, data: dict, operation_type: str):
    client = client_init_json()

    spread = None
    if operation_type == "Аренда":
        spread = get_table_by_url(client, config.report_sheet.rent_report_sheet_link)
    elif operation_type == "Покупка":
        spread = get_table_by_url(client, config.report_sheet.buy_report_sheet_link)

    fill_row_with_data(spread, worksheet_name=MONTHS_DICT[month], data=data)
    time.sleep(2)

