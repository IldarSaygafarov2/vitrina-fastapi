import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from config.loader import load_config
from infrastructure.database.models import User
from infrastructure.database.setup import create_engine, create_session_pool


print("addfsaf")


async def add_mock_user(session: AsyncSession):
    user = User(
        first_name="Ildar",
        lastname="Saygafarov",
        phone_number="111111111",
        tg_username="sayildar",
        role="realtor",
    )

    session.add_all([user])
    await session.commit()


async def main():
    config = load_config(".env")
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine=engine)

    async with session_pool() as session:
        await add_mock_user(session=session)


asyncio.run(main())
