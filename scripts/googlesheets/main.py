import asyncio

import gspread

from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from tgbot.misc.constants import MONTHS_DICT, ROW_FIELDS, ROW_FIELDS_V2
from tgbot.utils.google_sheet import add_row_titles, create_worksheets

config = load_config(".env")

user_account = gspread.oauth(
    credentials_filename=config.google_sheet.user_account_credentials_filename
)


async def create_spreadsheet_for_group_directors(session):
    repo = RequestsRepo(session)
    group_directors = await repo.users.get_users_by_role("GROUP_DIRECTOR")

    for group_director in group_directors:
        agents = await repo.users.get_director_agents(group_director.tg_chat_id)

        for agent in agents:
            if agent.spreadsheet_rent_url and agent.spreadsheet_buy_url:
                continue

            spreadsheet_rent = user_account.create(f"Аренда-{agent.fullname}")
            spreadsheet_buy = user_account.create(f"Продажа-{agent.fullname}")

            print(f"created table for agent: {agent.fullname}")
            row_titles = list(map(str.title, ROW_FIELDS_V2))

            create_worksheets(
                spread=spreadsheet_rent,
                worksheet_names=list(MONTHS_DICT.values()),
            )
            add_row_titles(spreadsheet_rent, row_titles)

            await asyncio.sleep(10)
            create_worksheets(
                spread=spreadsheet_buy,
                worksheet_names=list(MONTHS_DICT.values()),
            )
            # row titles of table
            add_row_titles(spreadsheet_buy, row_titles)

            await asyncio.sleep(10)
            print(f"added worksheets for agent: {agent.fullname}")

            await repo.users.update_user(
                agent.id,
                spreadsheet_rent_url=spreadsheet_rent.url,
                spreadsheet_buy_url=spreadsheet_buy.url,
            )

            print("Spreadsheets generetating")


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await create_spreadsheet_for_group_directors(session)


if __name__ == "__main__":
    asyncio.run(main())
    print("Spreadsheets created")
