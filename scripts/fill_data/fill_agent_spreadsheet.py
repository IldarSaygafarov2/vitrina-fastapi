import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from tgbot.utils.google_sheet import (
    fill_row_with_data,
    get_oauth_user,
    get_table_by_url,
)
from tgbot.utils.helpers import get_month_from_datetime_str

from tgbot.misc.constants import MONTHS_DICT

config = load_config(".env")

"""

название
район
тип недвижимости
ремонт
адрес
цена
(кол-во комнат/этаж/этажность)
квадратура
пользователь
статус модерации
дата добавления
уникальный ID

"""

FRONTEND_ADVERTISEMENT_URL = "https://ivitrina-nedvizhimosti.com/apartament/{id}"


async def fill_agent_spreadsheet(session: AsyncSession):
    repo = RequestsRepo(session)

    client = get_oauth_user()

    agents = await repo.users.get_users_by_role(role="REALTOR")

    data = {}
    for agent in agents:
        items = await repo.advertisements.get_user_advertisements(user_id=agent.id)

        if not items:
            continue

        data[agent.tg_username] = {}
        data[agent.tg_username]["rent_items"] = []
        data[agent.tg_username]["buy_items"] = []

        for item in items:
            item_data = {
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
            operation_type = item.operation_type.value

            if operation_type == "Аренда":
                data[agent.tg_username]["rent_items"].append(item_data)
            elif operation_type == "Покупка":
                data[agent.tg_username]["buy_items"].append(item_data)

        data[agent.tg_username]["rent_url"] = agent.spreadsheet_rent_url
        data[agent.tg_username]["buy_url"] = agent.spreadsheet_buy_url

    for _, agent_data in data.items():
        rent_table = get_table_by_url(client, url=agent_data["rent_url"])
        buy_table = get_table_by_url(client, url=agent_data["buy_url"])

        for rent_item in agent_data["rent_items"]:
            month = get_month_from_datetime_str(rent_item["дата добавления"])
            fill_row_with_data(rent_table, MONTHS_DICT[month], data=rent_item)

        for buy_item in agent_data["buy_items"]:
            month = get_month_from_datetime_str(buy_item["дата добавления"])
            fill_row_with_data(buy_table, MONTHS_DICT[month], data=buy_item)

    print("Done")


async def main():
    engine = create_engine(config.db)
    session = create_session_pool(engine)

    async with session() as session_pool:
        await fill_agent_spreadsheet(session_pool)


if __name__ == "__main__":
    asyncio.run(main())
