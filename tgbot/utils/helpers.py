from aiogram import Bot
from aiogram.types import InputMediaPhoto

from backend.app.config import config
from tgbot.misc.enums import RentForumTopicEnum


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
    if 100 < int(price) < 200:
        await bot.send_media_group(
            chat_id=config.tg_bot.supergroup_id,
            message_thread_id=RentForumTopicEnum.TOPIC_100_200.value[0],
            media=media_group
        )
    elif 200 < int(price) < 200:
        await bot.send_media_group(
            chat_id=config.tg_bot.supergroup_id,
            message_thread_id=RentForumTopicEnum.TOPIC_200_300.value[0],
            media=media_group
        )
    elif 300 < int(price) < 400:
        await bot.send_media_group(
            chat_id=config.tg_bot.supergroup_id,
            message_thread_id=RentForumTopicEnum.TOPIC_300_400.value[0],
            media=media_group
        )