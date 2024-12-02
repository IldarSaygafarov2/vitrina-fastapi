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
