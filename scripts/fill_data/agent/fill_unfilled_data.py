import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.utils.helpers import get_chosen_agent
from infrastructure.database.setup import create_engine, create_session_pool
from config.loader import load_config


config = load_config(".env")


async def fill_unfilled_data(session: AsyncSession):
    repo = RequestsRepo(session)

    chosen_agent = await get_chosen_agent(repo)

    print(chosen_agent)


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_unfilled_data(session)


if __name__ == "__main__":
    asyncio.run(main())
