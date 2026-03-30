from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class GoogleSheetConfig:
    spreadsheet_id: str
    user_account_credentials_filename: str
    # JWT пользователя после gspread.oauth (для Celery: писать в таблицы, созданные личным аккаунтом)
    oauth_token_path: Optional[str] = None

    @staticmethod
    def from_env(env: Env) -> "GoogleSheetConfig":
        token = env.str("GOOGLE_SHEETS_OAUTH_TOKEN_PATH", default="").strip()
        return GoogleSheetConfig(
            spreadsheet_id=env.str("SPREADSHEET_ID"),
            user_account_credentials_filename=env.str(
                "USER_ACCOUNT_CREDENTIALS_FILENAME"
            ),
            oauth_token_path=token or None,
        )


@dataclass
class ReportSheetConfig:
    rent_report_sheet_link: str
    buy_report_sheet_link: str

    config_filename: str
    # Папка в Drive пользователя, расшаренная на сервисный аккаунт (иначе create() падает по квоте)
    drive_spreadsheets_folder_id: Optional[str] = None

    @staticmethod
    def from_env(env: Env) -> "ReportSheetConfig":
        folder = env.str("GOOGLE_DRIVE_SPREADSHEETS_FOLDER_ID", default="").strip()
        return ReportSheetConfig(
            rent_report_sheet_link=env.str("RENT_REPORT_SHEET_LINK"),
            buy_report_sheet_link=env.str("BUY_REPORT_SHEET_LINK"),
            config_filename=env.str("REPORT_SHEET_CONFIG"),
            drive_spreadsheets_folder_id=folder or None,
        )
