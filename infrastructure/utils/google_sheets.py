import gspread
from gspread.cell import Cell
from gspread.spreadsheet import Spreadsheet

from config.constants import ROW_FIELDS_V2
from tgbot.utils.google_sheet import get_oauth_user, get_table_by_url

user_account = get_oauth_user()


def get_row_items(table_url, sheet):
    table = get_table_by_url(user_account, table_url)
    worksheet = table.worksheet(sheet)
    return worksheet.row_values(1)


def check_value_missing_in_row(table_url, sheet_name, value):
    row_values = get_row_items(table_url, sheet_name)
    row_values = list(map(str.lower, row_values))
    return value.lower() in row_values


class GoogleSheetService:
    def __init__(self, table: Spreadsheet) -> None:
        self.table = table

    def get_row_values(self, sheet_name: str, row_number: int = 1) -> list:
        worksheet = self.table.worksheet(sheet_name)
        return worksheet.row_values(row_number)

    def is_value_missing_in_row(self, sheet_name: str, value: str) -> bool:
        row_values = self.get_row_values(sheet_name)
        row_values = list(map(str.lower, row_values))
        if value not in row_values:
            return True
        return False

    def add_missing_value_in_row(
        self,
        sheet_name: str,
        value: str,
        operation_type: str,
    ):
        if not self.is_value_missing_in_row(sheet_name, value):
            print("value not missing skip")
            return

        row_values = self.get_row_values(sheet_name)
        cell_new_value = Cell(row=1, col=len(row_values) + 1, value=value.capitalize())
        self.table.worksheet(sheet_name).update_cells([cell_new_value])
        print(
            f"added missing value to worksheet '{sheet_name}' for operation type '{operation_type}' "
        )
