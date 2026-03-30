import asyncio

import gspread

from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from tgbot.misc.constants import MONTHS_DICT, ROW_FIELDS
from tgbot.utils.google_sheet import add_row_titles, create_worksheets

config = load_config(".env")

user_account = gspread.oauth(
    credentials_filename=config.google_sheet.user_account_credentials_filename
)


async def create_spreadsheet_for_group_directors(session):
    repo = RequestsRepo(session)
    group_directors = await repo.users.get_users_by_role("group_director")

    for group_director in group_directors:
        if group_director.has_spreadsheet:
            continue
        spreadsheet_rent = user_account.create(f"Аренда-{group_director.fullname}")
        spreadsheet_buy = user_account.create(f"Продажа-{group_director.fullname}")

        create_worksheets(spreadsheet_buy, list(MONTHS_DICT.values()))
        create_worksheets(spreadsheet_rent, list(MONTHS_DICT.values()))
        add_row_titles(spreadsheet_buy, list(ROW_FIELDS.values()))
        add_row_titles(spreadsheet_rent, list(ROW_FIELDS.values()))

        # Ссылки всегда пишем в БД; Celery (fill_report) дублирует строки в эти таблицы при модерации.
        await repo.users.update_user(
            group_director.id,
            has_spreadsheet=True,
            group_rent_sheet_url=spreadsheet_rent.url,
            group_buy_sheet_url=spreadsheet_buy.url,
        )
        if group_director.tg_chat_id is not None:
            await repo.users.sync_realtors_group_sheet_urls(
                group_director.tg_chat_id,
                spreadsheet_rent.url,
                spreadsheet_buy.url,
            )
        print(
            f"Spreadsheet created for {group_director.fullname}\n"
            f"  Аренда:  {spreadsheet_rent.url}\n"
            f"  Продажа: {spreadsheet_buy.url}"
        )


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await create_spreadsheet_for_group_directors(session)


if __name__ == "__main__":
    asyncio.run(main())
    print("Spreadsheets created")
