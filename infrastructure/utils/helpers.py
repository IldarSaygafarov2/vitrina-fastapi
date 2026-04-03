from datetime import datetime
import random

from config.loader import FRONTEND_ADVERTISEMENT_URL


def generate_code():
    return str(random.randint(100000, 999999))


async def get_unique_code(repo):
    unique_codes = await repo.advertisements.get_all_unique_ids()
    while True:
        code = generate_code()

        if code not in unique_codes:
            return code


def generate_item_for_sheet_table(item):
    return {
        "название": item.name,
        "район": item.district.name,
        "тип недвижимости": item.property_type.value,
        "ремонт": item.repair_type.value,
        "адрес": item.address,
        "к/э/э": f"{item.rooms_quantity}/{item.floor_from}/{item.floor_to}",
        "квадратура": item.quadrature,
        "пользователь": item.user.fullname,
        "статус модерации": item.is_moderated,
        "дата добавления": item.created_at.strftime("%d.%m.%Y %H:%M:%S"),
        "уникальный ID": item.unique_id,
        "ссылка на сайт": FRONTEND_ADVERTISEMENT_URL.format(id=item.id),
    }


def get_month_from_datetime_str(datetime_str: str) -> int:
    dt = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M:%S")
    return dt.month
