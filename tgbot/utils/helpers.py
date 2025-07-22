from aiogram.types import InputMediaPhoto

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