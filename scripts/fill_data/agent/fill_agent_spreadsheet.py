import asyncio
import json

from sqlalchemy.ext.asyncio import AsyncSession

from config.loader import FRONTEND_ADVERTISEMENT_URL, load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.utils.helpers import (
    generate_item_for_sheet_table,
    get_month_from_datetime_str,
)
from tgbot.misc.constants import MONTHS_DICT
from tgbot.utils.google_sheet import (
    fill_row_with_data,
    get_oauth_user,
    get_table_by_url,
)

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


client = get_oauth_user()


async def fill_agent_spreadsheet(session: AsyncSession):
    repo = RequestsRepo(session)

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
            item_data = generate_item_for_sheet_table(item)
            operation_type = item.operation_type.value

            if operation_type == "Аренда":
                data[agent.tg_username]["rent_items"].append(item_data)
            elif operation_type == "Покупка":
                data[agent.tg_username]["buy_items"].append(item_data)

        data[agent.tg_username]["rent_url"] = agent.spreadsheet_rent_url
        data[agent.tg_username]["buy_url"] = agent.spreadsheet_buy_url

    for agent_username, agent_data in data.items():
        rent_table = get_table_by_url(client, url=agent_data["rent_url"])
        buy_table = get_table_by_url(client, url=agent_data["buy_url"])

        for rent_idx, rent_item in enumerate(agent_data["rent_items"], start=1):
            month = get_month_from_datetime_str(rent_item["дата добавления"])
            print(f"Adding rent item #{rent_idx}\nAgent: {agent_username}")
            fill_row_with_data(rent_table, MONTHS_DICT[month], data=rent_item)
            await asyncio.sleep(1.5)

        for buy_idx, buy_item in enumerate(agent_data["buy_items"], start=1):
            month = get_month_from_datetime_str(buy_item["дата добавления"])
            print(f"Adding rent item #{buy_idx}\nAgent: {agent_username}")
            fill_row_with_data(buy_table, MONTHS_DICT[month], data=buy_item)
            await asyncio.sleep(1.5)

    with open("agents_data.json", mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print("Done")


async def main():
    engine = create_engine(config.db)
    session = create_session_pool(engine)

    async with session() as session_pool:
        await fill_agent_spreadsheet(session_pool)


if __name__ == "__main__":
    asyncio.run(main())
