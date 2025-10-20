import time

from backend.app.config import config
from celery_tasks.app import celery_app
from tgbot.misc.constants import MONTHS_DICT
from tgbot.utils.google_sheet import (
    client_init_json,
    get_table_by_url,
    fill_row_with_data,
)
from tgbot.utils.helpers import deserialize_media_group
from tgbot.keyboards.user.inline import is_advertisement_actual_kb


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


@celery_app.task
def send_delayed_message(chat_id, media_group):
    from aiogram import Bot
    import asyncio

    async def send_media_group():
        bot = Bot(token=config.tg_bot.token)
        _media = deserialize_media_group(media_group)
        await bot.send_media_group(chat_id=chat_id, media=_media)
        await bot.session.close()

    asyncio.run(send_media_group())


@celery_app.task
def remind_agent_to_update_advertisement(unique_id, agent_chat_id: int, advertisement_id: int):
    import asyncio
    from aiogram import Bot

    async def send_reminder():
        bot = Bot(token=config.tg_bot.token)
        msg = f"""
Объявление: №{unique_id} является актуальным?
"""
        await bot.send_message(
            agent_chat_id, msg, parse_mode='HTML', reply_markup=is_advertisement_actual_kb(advertisement_id)
        )
        await bot.session.close()
    asyncio.run(send_reminder())
