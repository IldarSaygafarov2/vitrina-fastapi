import asyncio
import pprint

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
    sheet_service = GoogleSheetService(table=spreadsheet)

    for month, month_number in MONTHS_DICT_REVERSED.items():
        print(f"Filling data for month: '{month}'")
        agent_advertisements = (
            await repo.advertisements.get_user_advertisements_by_month(
                user_id=chosen_agent.get("agent_id"),
                month=month_number,
                operation_type=operation_type,
            )
        )
        # сконвертированные в словарь объявления
        agent_advertisements = [
            generate_item_for_sheet_table(item) for item in agent_advertisements
        ]
        agent_sheet_advertisements, _ = sheet_service.get_sheet_values(month)
        sheet_advs_ids = [
            item.get("Уникальный Id") for item in agent_sheet_advertisements
        ]
        print(sheet_advs_ids)

        advertisements = [
            item
            for item in agent_advertisements
            if int(item.get("уникальный ID")) in sheet_advs_ids
        ]
        print(advertisements, len(advertisements))
        # уникальный ID
        # Уникальный Id

        return
        if not agent_advertisements:
            continue

        owners_phones = [adv.get("номер собственника") for adv in agent_advertisements]
        sheet_service.bulk_update_cells(
            month,
            owners_phones,
            col_number=len(ROW_FIELDS_V2),
        )
        await asyncio.sleep(2)

        # _, month_total_sheet_values = sheet_service.get_sheet_values(month)

        # for i in range(1, month_total_sheet_values + 1):

        #     owner_number = agent_advertisements[i - 1].get("номер собственника")
        #     sheet_service.add_missing_value_in_row(
        #         month, owner_number, row_number=i + 1
        #     )
        #     await asyncio.sleep(3)


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_missing_col(session)


if __name__ == "__main__":
    asyncio.run(main())
