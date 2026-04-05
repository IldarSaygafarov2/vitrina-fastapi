import asyncio
from typing import Any
from pprint import pprint

from sqlalchemy.ext.asyncio import AsyncSession

from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.database.models import User
from tgbot.misc.constants import MONTHS_DICT
from tgbot.utils.google_sheet import (
    fill_row_with_data,
    get_oauth_user,
    get_table_by_url,
    get_sheet_values,
)
from infrastructure.utils.helpers import generate_item_for_sheet_table

config = load_config(".env")


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


def _generate_agents_fullnames_str(agents_data: dict) -> str:
    result = ""

    for agent_id, data in agents_data.items():
        result += f"{agent_id}: {data['fullname']}\n"
    return result


def _generate_agents_dict(agents_list: list[User]):
    result = {}
    for agent in agents_list:
        result[agent.id] = {
            "fullname": agent.fullname,
            "rent_url": agent.spreadsheet_rent_url,
            "buy_url": agent.spreadsheet_buy_url,
        }
    return result


def get_data_from_dict(key, data_dict: dict) -> Any:
    """Get data by key from dict."""
    chosen_item = data_dict.get(key)
    if chosen_item is None:
        raise KeyError("key not found")
    return chosen_item


async def fill_agent_report_data(session: AsyncSession):
    user_account = get_oauth_user()
    repo = RequestsRepo(session)

    # подготовка данных агентов
    agents: list[User] = await repo.users.get_users_by_role(role="REALTOR")
    agents_dict = _generate_agents_dict(agents)
    agents_fullnames_str = _generate_agents_fullnames_str(agents_dict)

    # получение определенного агента
    print(agents_fullnames_str)
    agent_id = int(input("write agent id: "))
    chosen_agent = get_data_from_dict(agent_id, agents_dict)

    # подготовка и получение месяца
    enum_months = "\n".join([f"{idx}. {month}" for idx, month in MONTHS_DICT.items()])
    print(enum_months)
    month_number = int(input("write month number: "))
    chosen_month = get_data_from_dict(month_number, MONTHS_DICT)

    # получение типа операции
    operation_type = input("choose operation type: ")
    # operation_type_value = "Аренда" if operation_type == "rent" else "Продажа"

    report_url = (
        chosen_agent.get("rent_url")
        if operation_type == "rent"
        else chosen_agent.get("buy_url")
    )

    sheet_advertisements = get_current_sheet_data(
        client=user_account,
        table_url=report_url,
        sheet_name=chosen_month,
    )

    agent_month_advertisements = (
        await repo.advertisements.get_user_advertisements_by_month(
            user_id=agent_id,
            month=month_number,
            operation_type=operation_type.upper(),
        )
    )
    agent_advertisements = [
        generate_item_for_sheet_table(item) for item in agent_month_advertisements
    ]

    missing_advertisements = get_missing_advertisements(
        sheet_advertisements=sheet_advertisements,
        agent_advertisements=agent_advertisements,
    )

    if not missing_advertisements:
        print("missing advertisements not found")
        return

    print(
        f"Agent: '{chosen_agent['fullname']}' has {len(missing_advertisements)} not added advertisements"
    )
    for advertisement_item in missing_advertisements:
        table = get_table_by_url(user_account, report_url)
        fill_row_with_data(table, chosen_month, data=advertisement_item)
        await asyncio.sleep(1.4)


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_agent_report_data(session)


if __name__ == "__main__":
    asyncio.run(main())
