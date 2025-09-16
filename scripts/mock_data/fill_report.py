import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import config
from infrastructure.database.repo.requests import RequestsRepo
from backend.core.interfaces.advertisement import AdvertisementForReportDTO
from infrastructure.database.setup import create_engine, create_session_pool
from tgbot.misc.constants import MONTHS_DICT
from tgbot.utils.google_sheet import client_init_json, get_table_by_url, fill_row_with_data
from tgbot.utils.helpers import correct_advertisement_dict


async def fill_report(session: AsyncSession) -> None:
    repo = RequestsRepo(session)

    client = client_init_json()
    rent_spread = get_table_by_url(client, config.report_sheet.full_rent_report_sheet_link)

    advertisements = await repo.advertisements.get_all_moderated_advertisements()

    for advertisement in advertisements:
        item = AdvertisementForReportDTO.model_validate(advertisement, from_attributes=True)
        month = item.created_at.month
        item = correct_advertisement_dict(item.model_dump())
        if item.get('operation_type').lower() == 'аренда':
            fill_row_with_data(rent_spread, MONTHS_DICT[month], item)
            await asyncio.sleep(1.5)
            print(f'Added advertisement with unique_id={item.get("unique_id")}')




async def main() -> None:
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_report(session)


asyncio.run(main())

