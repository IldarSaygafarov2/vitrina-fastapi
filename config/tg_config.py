from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    rent_channel_name: str
    buy_channel_name: str

    @staticmethod
    def from_env(env: Env) -> "TgBot":
        return TgBot(
            token=env.str("BOT_API_TOKEN"),
            rent_channel_name=env.str("RENT_CHANNEL"),
            buy_channel_name=env.str("BUY_CHANNEL"),
        )
