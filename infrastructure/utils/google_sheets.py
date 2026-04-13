import gspread
from gspread.cell import Cell
from gspread.spreadsheet import Spreadsheet

from config.constants import ROW_FIELDS_V2
from tgbot.utils.google_sheet import get_oauth_user

user_account = get_oauth_user()


class GoogleSheetService:
    def __init__(self, table: Spreadsheet) -> None:
        self.table = table

    def get_row_values(self, sheet_name: str, row_number: int = 1) -> list:
        worksheet = self.table.worksheet(sheet_name)
        return worksheet.row_values(row_number)

    def get_sheet_values(self, sheet_name: str):
        worksheet = self.table.worksheet(sheet_name)
        headers = list(map(str.title, ROW_FIELDS_V2))
        headers[-1] = headers[-1].capitalize()
        records = worksheet.get_all_records(expected_headers=headers)
        return records, len(records)

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
        row_number: int = 1,
    ):
        if not self.is_value_missing_in_row(sheet_name, value):
            print("value not missing skip")
            return

        row_values = self.get_row_values(sheet_name)
        cell_new_value = Cell(
            row=row_number,
            col=len(row_values),
            value=value,
        )
        self.table.worksheet(sheet_name).update_cells([cell_new_value])
        print(f"added missing value '{value}' to worksheet '{sheet_name}' ")

    def bulk_update_cells(self, sheet_name: str, values, col_number):
        """Множественное обновление пустых ячеек"""
        cells_for_update = [
            Cell(row=i + 1, col=col_number, value=value)
            for i, value in enumerate(values, start=1)
        ]
        self.table.worksheet(sheet_name).update_cells(cells_for_update)
        print(f"added values:", *values, f"to '{sheet_name}' ")
