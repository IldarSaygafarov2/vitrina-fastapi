import json

from aiogram import Bot
from aiogram.types import InputMediaPhoto

from backend.app.config import config


def read_json(file_path: str):
    with open(file_path, mode='r', encoding='utf-8') as f:
        return json.load(f)


def filter_digits(message: str):
    return "".join(list(filter(lambda i: i.isdigit(), message)))


def get_media_group(photos, message: str | None = None) -> list[InputMediaPhoto]:

    media_group: list[InputMediaPhoto] = [
        (
            InputMediaPhoto(media=img, caption=message)
            if i == 0
            else InputMediaPhoto(media=img)
        )
        for i, img in enumerate(photos)
    ]
    return media_group





async def send_message_to_rent_topic(
        bot: Bot,
        price: int,
        media_group: list[InputMediaPhoto],
):
    topic_data = config.super_group.make_forum_topics_data()
    prices = list(topic_data.items())
    supergroup_id = config.tg_bot.supergroup_id

    for thread_id, _price in prices:
        a, b = _price

        price_range = list(range(a, b))
        if price not in price_range:
            continue
        await bot.send_media_group(
            chat_id=supergroup_id,
            message_thread_id=thread_id,
            media=media_group
        )




