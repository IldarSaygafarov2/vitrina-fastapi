import os
from config.loader import load_config

config = load_config()


def send_media_from_html():
    pass


def prepare_media_group_for_request(photos, message):
    media = []
    files = {}

    for i, photo in enumerate(photos):
        filename = os.path.basename(photo)
        files[filename] = open(photo, "rb")

        media_item = {
            "type": "photo",
            "media": f"attach://{filename}",
            "parse_mode": "HTML",
        }
        if i == 0:
            media_item["caption"] = message
        media.append(media_item)

    return media, files


async def send_message_to_rent_topic(
    price: int,
    operation_type: str,
    media_group,
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

    for thread_id, _price in prices:
        a, b = _price

        price_range = list(range(a, b))
        if price not in price_range:
            continue

        # await bot.send_media_group(
        #     chat_id=supergroup_id, message_thread_id=thread_id, media=media_group
        # )
    print("SENT TO SUPERGROUP")
