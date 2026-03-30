import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from gspread import Client, Spreadsheet, authorize, service_account

from backend.app.config import config
from tgbot.misc.constants import MONTHS_DICT, ROW_FIELDS

_OAUTH_SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
)


def client_init_json() -> Client:
    return service_account(filename=config.report_sheet.config_filename)


def gspread_client_for_director_tables() -> Client:
    """
    Таблицы руководителя часто созданы через OAuth (личный Google).
    Если задан GOOGLE_SHEETS_OAUTH_TOKEN_PATH с token.json — используем его в Celery;
    иначе — сервисный аккаунт (таблицы должны быть расшарены на client_email из JSON).
    """
    raw = config.google_sheet.oauth_token_path
    if raw:
        path = Path(raw).expanduser()
        if path.is_file():
            creds = Credentials.from_authorized_user_file(
                str(path), scopes=list(_OAUTH_SCOPES)
            )
            return authorize(creds)
    return client_init_json()


def get_table_by_url(client: Client, url: str) -> Spreadsheet:
    return client.open_by_url(url)


def create_worksheets(spread: Spreadsheet, worksheet_names: list[str] = None):
    current_worksheets = [sheet.title for sheet in spread.worksheets()]

    for worksheet_name in worksheet_names:
        if worksheet_name in current_worksheets:
            continue

        spread.add_worksheet(worksheet_name, rows=1000, cols=26)

    print(f"Created {len(worksheet_names)} worksheets")


def add_row_titles(spread: Spreadsheet, data):
    worksheets = spread.worksheets()
    for worksheet in worksheets:
        worksheet.append_row(data)


def update_row_values(spread: Spreadsheet, worksheet_name: str, values: list):
    worksheet = spread.worksheet(worksheet_name)
    all_values_count = len(worksheet.get_all_values())
    for item in values:
        item = list(item.values())
        worksheet.insert_row(item, index=all_values_count + 1)
        print(f"Added row: {item}")
        time.sleep(2)


def fill_row_with_data(spread: Spreadsheet, worksheet_name: str, data: dict):
    worksheet = spread.worksheet(worksheet_name)
    total_values = len(worksheet.get_all_values())
    data_values = list(data.values())
    worksheet.insert_row(data_values, index=total_values + 1)
    print(f"Added row: {data_values}")


def get_sheet_values(spread: Spreadsheet, worksheet_name: str):
    worksheet = spread.worksheet(worksheet_name)
    return worksheet.get_all_records()


# def main() -> None:
#     client = client_init_json()
#     buy_spread = get_table_by_url(client, config.report_sheet.buy_report_sheet_link)
#     rent_spread = get_table_by_url(client, config.report_sheet.rent_report_sheet_link)
#     print(buy_spread, rent_spread)
#     create_worksheets(buy_spread, list(MONTHS_DICT.values()))
#     create_worksheets(rent_spread, list(MONTHS_DICT.values()))
#     add_row_titles(buy_spread, list(ROW_FIELDS.values()))
#     add_row_titles(rent_spread, list(ROW_FIELDS.values()))
#
#
#     # full_rent_report_spread = get_table_by_url(client, config.report_sheet.full_rent_report_sheet_link)
#     # buy_full_report_spread = get_table_by_url(client, config.report_sheet.full_buy_report_sheet_link)
#     # # create_worksheets(full_rent_report_spread, list(MONTHS_DICT.values()))
#     # create_worksheets(buy_full_report_spread, list(MONTHS_DICT.values()))
#     # # add_row_titles(full_rent_report_spread, list(ROW_FIELDS.values()))
#     # add_row_titles(buy_full_report_spread, list(ROW_FIELDS.values()))
#     print('done')
#
#
# if __name__ == '__main__':
#     main()
