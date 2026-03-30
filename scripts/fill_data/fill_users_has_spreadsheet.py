import asyncio

from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool

config = load_config(".env")


async def fill_users_has_spreadsheet(session):
    repo = RequestsRepo(session)
    directors = await repo.users.get_users_by_role("GROUP_DIRECTOR")
    for director in directors:
        director.has_spreadsheet = True
    await session.commit()


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_users_has_spreadsheet(session)


asyncio.run(main())
