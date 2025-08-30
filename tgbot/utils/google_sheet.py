from gspread import Client, Spreadsheet, service_account

from backend.app.config import config

MONTHS = [
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентябрь',
    'Октябрь',
    'Ноябрь',
    'Декабрь',
]


def client_init_json() -> Client:
    return service_account(filename=config.report_sheet.config_filename)


def get_table_by_url(client: Client, url: str) -> Spreadsheet:
    return client.open_by_url(url)


def create_worksheets(spread: Spreadsheet, worksheet_names: list[str] = None):
    current_worksheets = [sheet.title for sheet in spread.worksheets()]

    for worksheet_name in worksheet_names:
        if worksheet_name in current_worksheets:
            continue

        spread.add_worksheet(worksheet_name, rows=1, cols=1)

    print(f'Created {len(worksheet_names)} worksheets')


def main():
    client = client_init_json()
    spreadsheet = get_table_by_url(client, config.report_sheet.report_sheet_link)
    create_worksheets(spreadsheet, MONTHS)


if __name__ == '__main__':
    main()
