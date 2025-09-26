import asyncio

from backend.core.interfaces.advertisement import AdvertisementForReportDTO
from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool

config = load_config(".env")


async def fill_report(session):
    repo = RequestsRepo(session)

    advertisements = await repo.advertisements.get_advertisements_by_month(4)
    advertisements = [
        AdvertisementForReportDTO.model_validate(obj, from_attributes=True).model_dump()
        for obj in advertisements
    ]


async def main() -> None:
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_report(session)


asyncio.run(main())
