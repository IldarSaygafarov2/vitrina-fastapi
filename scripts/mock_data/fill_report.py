import asyncio
from pprint import pprint

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import config
from backend.core.interfaces.advertisement import AdvertisementForReportDTO
from infrastructure.database.models import Advertisement
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from tgbot.misc.constants import MONTHS_DICT
from tgbot.utils.google_sheet import client_init_json, get_table_by_url, fill_row_with_data, get_sheet_values
from tgbot.utils.helpers import correct_advertisement_dict


def split_list(lst, n_parts):
    k, m = divmod(len(lst), n_parts)  # k - базовый размер части, m - сколько частей получат +1 элемент
    result = []
    start = 0
    for i in range(n_parts):
        end = start + k + (1 if i < m else 0)
        result.append(lst[start:end])
        start = end
    return result


async def fill_data(spread, objects: list[Advertisement]):
    for obj in objects:
        item = AdvertisementForReportDTO.model_validate(obj, from_attributes=True)
        month = item.created_at.month
        item = correct_advertisement_dict(item.model_dump())
        fill_row_with_data(spread, MONTHS_DICT[month], item)
        await asyncio.sleep(1)
        print(f'Added advertisement with unique_id={item.get("unique_id")}')



async def fill_report(session: AsyncSession) -> None:
    repo = RequestsRepo(session)
    client = client_init_json()
    rent_spread = get_table_by_url(client, config.report_sheet.rent_report_sheet_link)
    data = {}
    for month_number, month_name in MONTHS_DICT.items():
        items = get_sheet_values(rent_spread, month_name)
        data[month_name] = items

    unique_ids_by_months = {}
    for month, items in data.items():
        unique_ids_by_months[month] = []
        for item in items:
            unique_ids_by_months[month].append(item.get('unique_id'))

    print(unique_ids_by_months)



    # rent_advertisements = await repo.advertisements.get_all_moderated_advertisements(operation_type='RENT')
    # buy_advertisements = await repo.advertisements.get_all_moderated_advertisements(operation_type='BUY')
    #
    # tasks = [await fill_data(rent_spread, rent_advertisements), await fill_data(buy_spread, buy_advertisements)]
    # await asyncio.gather(*tasks)

async def main() -> None:
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_report(session)


asyncio.run(main())

