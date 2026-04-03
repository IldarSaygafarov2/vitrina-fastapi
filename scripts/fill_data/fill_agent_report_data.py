import asyncio

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
)
from infrastructure.utils.helpers import (
    get_month_from_datetime_str,
    generate_item_for_sheet_table,
)

config = load_config(".env")


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


async def fill_agent_report_data(session: AsyncSession):
    user_account = get_oauth_user()

    repo = RequestsRepo(session)

    agents: list[User] = await repo.users.get_users_by_role(role="REALTOR")

    agents_dict = _generate_agents_dict(agents)
    agents_fullnames_str = _generate_agents_fullnames_str(agents_dict)

    print(agents_fullnames_str)
    agent_id = int(input("write agent id: "))
    chosen_agent = agents_dict.get(agent_id)
    if chosen_agent is None:
        print("Agent not found")
        return

    agent_advertisements = await repo.advertisements.get_user_advertisements(
        user_id=agent_id
    )
    total_advertisements = len(agent_advertisements)

    print(
        f"Agent: '{chosen_agent['fullname']}' has {total_advertisements} advertisements"
    )
    for idx, advertisement in enumerate(agent_advertisements, start=1):
        operation_type = advertisement.operation_type.value
        item = generate_item_for_sheet_table(advertisement)
        month = get_month_from_datetime_str(item["дата добавления"])

        table_url = (
            chosen_agent["rent_url"]
            if operation_type == "Аренда"
            else chosen_agent["buy_url"]
        )
        table = get_table_by_url(user_account, table_url)
        print(f"{idx}. Operation type: {operation_type}")
        fill_row_with_data(table, MONTHS_DICT[month], data=item)
        await asyncio.sleep(1.4)


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_agent_report_data(session)


if __name__ == "__main__":
    asyncio.run(main())
