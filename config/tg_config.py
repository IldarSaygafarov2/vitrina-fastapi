from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str

    @staticmethod
    def from_env(env: Env) -> "TgBot":
        return TgBot(
            token=env.str("BOT_API_TOKEN"),
        )
