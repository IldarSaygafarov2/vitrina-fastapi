import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from config.constants import MONTHS_DICT
from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.utils.google_sheets import GoogleSheetService
from infrastructure.utils.helpers import get_chosen_agent
from tgbot.utils.google_sheet import get_oauth_user, get_table_by_url

config = load_config(".env")

user_account = get_oauth_user()


async def fill_unfilled_data(session: AsyncSession):
    repo = RequestsRepo(session)

    chosen_agent = await get_chosen_agent(repo)
    rent_table = get_table_by_url(user_account, url=chosen_agent.get("rent_url"))
    buy_table = get_table_by_url(user_account, url=chosen_agent.get("buy_url"))

    rent_table_service = GoogleSheetService(table=rent_table)
    buy_table_service = GoogleSheetService(table=buy_table)

    print(f'working with agent: {chosen_agent.get("fullname")}')
    for month in MONTHS_DICT.values():
        rent_table_service.add_missing_value_in_row(month, value="номер собственника")
        buy_table_service.add_missing_value_in_row(month, value="номер собственника")
        await asyncio.sleep(1.5)


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_unfilled_data(session)


if __name__ == "__main__":
    asyncio.run(main())


"""
TODO:
    1) получить всех агентов
    2) открыть таблицы (аренда,покупка)
    3) зайти в каждый лист для месяцов в таблицах
    4) проверить есть ли поле "имя собственника"
    5) если поле есть то пропустить лист
    6) если поля нет, то добавить его
"""
