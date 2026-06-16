import json
import os

import aiohttp
import requests

from config.constants import MEDIA_GROUP_URL
from config.loader import load_config

config = load_config()


def send_media_from_html(data, files):
    for f in files.values():
        f.seek(0)

    # async with aiohttp.ClientSession() as session:
    #     async with session.post(
    #         MEDIA_GROUP_URL.format(BOT_TOKEN=config.tg_bot.token),
    #         data=data,
    #         files=files,
    #     ) as response:
    #         print(f"Status: {response.status_code}")

    response = requests.post(
        MEDIA_GROUP_URL.format(BOT_TOKEN=config.tg_bot.token),
        data=data,
        files=files,
    )
    print(response.status_code, response.text)


def prepare_media_group_for_request(photos, message):
    media = []
    files = {}
    file_paths = {}
    for i, photo in enumerate(photos):

        filename = os.path.basename(photo)
        files[filename] = open(photo, "rb")
        file_paths[filename] = photo

        media_item = {
            "type": "photo",
            "media": f"attach://{filename}",
            "parse_mode": "HTML",
        }
        if i == 0:
            media_item["caption"] = message
        media.append(media_item)

    return media, files, file_paths


def send_message_to_rent_topic(
    price: int, operation_type: str, media_group, files
) -> None:
    """Отправляем сообщение в супер группу фильтруя по цене."""

    topic_data = config.super_group.make_forum_topics_data(operation_type)
    prices = list(topic_data.items())

    # supergroups ids
    rent_supergroup_id = config.super_group.rent_supergroup_id
    buy_supergroup_id = config.super_group.buy_supergroup_id

    supergroup_id = (
        rent_supergroup_id if operation_type == "Аренда" else buy_supergroup_id
    )

    data = {"chat_id": supergroup_id}

    for thread_id, _price in prices:
        a, b = _price

        price_range = list(range(a, b))

        if price not in price_range:
            continue

        data.update({"message_thread_id": thread_id, "media": json.dumps(media_group)})
        send_media_from_html(data=data, files=files)
    print("SENT TO SUPERGROUP")
