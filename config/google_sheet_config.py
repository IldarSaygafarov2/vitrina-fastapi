from dataclasses import dataclass

from environs import Env


@dataclass
class GoogleSheetConfig:
    spreadsheet_id: str

    @staticmethod
    def from_env(env: Env) -> "GoogleSheetConfig":
        return GoogleSheetConfig(
            spreadsheet_id=env.str("SPREADSHEET_ID"),
        )


@dataclass
class ReportSheetConfig:
    report_sheet_link: str
    config_filename: str

    @staticmethod
    def from_env(env: Env) -> "ReportSheetConfig":
        return ReportSheetConfig(
            report_sheet_link=env.str("REPORT_SHEET_LINK"),
            config_filename=env.str("REPORT_SHEET_CONFIG"),
        )