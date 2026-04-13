import random
from datetime import datetime

from config.constants import FRONTEND_ADVERTISEMENT_URL, MONTHS_DICT
from infrastructure.database.models import User, Advertisement
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.utils.google_sheet import get_sheet_values, get_table_by_url


def generate_code():
    return str(random.randint(100000, 999999))


async def get_unique_code(repo):
    unique_codes = await repo.advertisements.get_all_unique_ids()
    while True:
        code = generate_code()

        if code not in unique_codes:
            return code


def generate_item_for_sheet_table(item: Advertisement):
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
        "номер собственника": item.owner_phone_number,
    }


def get_month_from_datetime_str(datetime_str: str) -> int:
    dt = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M:%S")
    return dt.month


def get_data_from_dict(key, data_dict: dict):
    """Get data by key from dict."""
    chosen_item = data_dict.get(key)
    if chosen_item is None:
        raise KeyError("key not found")
    return chosen_item


def generate_agents_fullnames_str(agents_data: dict) -> str:
    result = ""

    for agent_id, data in agents_data.items():
        result += f"{agent_id}: {data['fullname']}\n"
    return result


def generate_agents_dict(agents_list: list[User]):
    result = {}
    for agent in agents_list:
        result[agent.id] = {
            "fullname": agent.fullname,
            "rent_url": agent.spreadsheet_rent_url,
            "buy_url": agent.spreadsheet_buy_url,
            "agent_id": agent.id,
        }
    return result


def get_current_sheet_data(client, table_url, sheet_name: str):
    table = get_table_by_url(client, table_url)
    data = get_sheet_values(table, sheet_name)
    return data


def get_missing_advertisements(sheet_advertisements, agent_advertisements):
    missing_ids = []
    sheet_advertisements_unique_ids = [
        item.get("Уникальный Id") for item in sheet_advertisements
    ]
    agent_advertisements_unique_ids = [
        int(item.get("уникальный ID")) for item in agent_advertisements
    ]

    for unique_id in agent_advertisements_unique_ids:
        if unique_id not in sheet_advertisements_unique_ids:
            missing_ids.append(unique_id)

    return [
        item
        for item in agent_advertisements
        if int(item.get("уникальный ID")) in missing_ids
    ]


async def get_chosen_agent(repo: RequestsRepo):
    agents: list[User] = await repo.users.get_users_by_role(role="REALTOR")
    agents_dict = generate_agents_dict(agents)
    agents_fullname_str = generate_agents_fullnames_str(agents_dict)
    print(agents_fullname_str)
    agent_id = int(input("write agent id: "))
    chosen_agent = get_data_from_dict(agent_id, agents_dict)
    return chosen_agent


def get_chosen_month():
    enum_months = "\n".join([f"{idx}. {month}" for idx, month in MONTHS_DICT.items()])
    print(enum_months)
    month_number = int(input("write month number: "))
    chosen_month = get_data_from_dict(month_number, MONTHS_DICT)
    return chosen_month
