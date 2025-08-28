from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    rent_channel_name: str
    buy_channel_name: str
    base_channel_name: str
    main_chat_id: int
    test_main_chat_id: int
    supergroup_id: int

    @staticmethod
    def from_env(env: Env) -> "TgBot":
        return TgBot(
            token=env.str("BOT_API_TOKEN"),
            rent_channel_name=env.str("RENT_CHANNEL"),
            buy_channel_name=env.str("BUY_CHANNEL"),
            base_channel_name=env.str("BASE_CHANNEL"),
            main_chat_id=env.int("MAIN_CHAT_ID"),
            test_main_chat_id=env.int("TEST_MAIN_CHAT_ID"),
            supergroup_id=env.int("SUPERGROUP_ID")
        )


@dataclass
class TgSuperGroupConfig:
    rent_supergroup_id: int
    buy_supergroup_id: int

    @staticmethod
    def from_env(env: Env) -> "TgSuperGroupConfig":
        return TgSuperGroupConfig(
            rent_supergroup_id=env.int('RENT_SUPERGROUP_ID'),
            buy_supergroup_id=env.int('BUY_SUPERGROUP_ID'),
        )
