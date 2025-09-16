# import asyncio
#
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from backend.app.config import config
# from backend.core.interfaces.advertisement import AdvertisementForReportDTO
# from infrastructure.database.repo.requests import RequestsRepo
# from infrastructure.database.setup import create_engine, create_session_pool
# from tgbot.misc.constants import MONTHS_DICT
# from tgbot.utils.google_sheet import client_init_json, get_table_by_url, fill_row_with_data
# from tgbot.utils.helpers import correct_advertisement_dict
# from multiprocessing import Process
#
#
# def split_list(lst, n_parts):
#     k, m = divmod(len(lst), n_parts)  # k - базовый размер части, m - сколько частей получат +1 элемент
#     result = []
#     start = 0
#     for i in range(n_parts):
#         end = start + k + (1 if i < m else 0)
#         result.append(lst[start:end])
#         start = end
#     return result
#
#
# def fill_data()
#
#
#
# async def fill_report(session: AsyncSession) -> None:
#     repo = RequestsRepo(session)
#
#     client = client_init_json()
#     rent_spread = get_table_by_url(client, config.report_sheet.full_rent_report_sheet_link)
#
#     advertisements = await repo.advertisements.get_all_moderated_advertisements()
#     l1, l2, l3 = split_list(advertisements, 3)
#     print(len(l1), len(l2), len(l3))
#
#
#     for advertisement in advertisements:
#         break
#         item = AdvertisementForReportDTO.model_validate(advertisement, from_attributes=True)
#         month = item.created_at.month
#         item = correct_advertisement_dict(item.model_dump())
#
#         if item.get('operation_type').lower() == 'аренда':
#             fill_row_with_data(rent_spread, MONTHS_DICT[month], item)
#             await asyncio.sleep(1.5)
#             print(f'Added advertisement with unique_id={item.get("unique_id")}')
#
#
#
#
# async def main() -> None:
#     engine = create_engine(config.db)
#     session_pool = create_session_pool(engine)
#
#     async with session_pool() as session:
#         await fill_report(session)
#
#
# asyncio.run(main())
#
