import asyncio
from pprint import pprint

from sqlalchemy.ext.asyncio import AsyncSession

from config.constants import MONTHS_DICT_REVERSED, ROW_FIELDS_V2
from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.utils.google_sheets import GoogleSheetService
from infrastructure.utils.helpers import (
    generate_item_for_sheet_table,
    get_chosen_agent,
    get_chosen_month,
)
from tgbot.utils.google_sheet import get_oauth_user, get_table_by_url

config = load_config(".env")

user_account = get_oauth_user()


async def fill_missing_col(session: AsyncSession):
    repo = RequestsRepo(session)

    chosen_agent = await get_chosen_agent(repo)
    print(chosen_agent)

    print("Write operation type: rent, buy")
    operation_type = input("operation type: ").upper()

    table_url = (
        chosen_agent.get("rent_url")
        if operation_type == "RENT"
        else chosen_agent.get("buy_url")
    )

    # google spreadsheet service
    spreadsheet = get_table_by_url(user_account, table_url)

    for month, month_number in MONTHS_DICT_REVERSED.items():
        print(f"working with: '{month}'")
        agent_advertisements = (
            await repo.advertisements.get_user_advertisements_by_month(
                user_id=chosen_agent.get("agent_id"),
                month=month_number,
                operation_type=operation_type,
            )
        )
        # сконвертированные в словарь объявления
        agent_advertisements = [
            list(generate_item_for_sheet_table(item).values())
            for item in agent_advertisements
        ]
        if not agent_advertisements:
            continue

        sheet = spreadsheet.worksheet(month)
        headers = list(map(str.title, ROW_FIELDS_V2))
        headers[-1] = headers[-1].capitalize()
        records = sheet.get_all_records(expected_headers=headers)

        if records:
            sheet.delete_rows(2, len(records))

        sheet.insert_rows(agent_advertisements, row=2)
        await asyncio.sleep(2)


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_missing_col(session)


if __name__ == "__main__":
    asyncio.run(main())
