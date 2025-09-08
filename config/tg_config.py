from dataclasses import dataclass

from environs import Env
import json


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
    rent_supergroup_id: str
    buy_supergroup_id: str

    rent_topic_thread_ids: str
    rent_topic_prices: str

    @staticmethod
    def from_env(env: Env) -> "TgSuperGroupConfig":
        return TgSuperGroupConfig(
            rent_supergroup_id=env.str('RENT_SUPERGROUP_ID'),
            buy_supergroup_id=env.str('BUY_SUPERGROUP_ID'),
            rent_topic_thread_ids=env.str('RENT_TOPIC_THREAD_IDS'),
            rent_topic_prices=env.str('RENT_TOPIC_PRICES'),
        )

    def get_rent_topic_thread_ids(self):
        return list(map(int, self.rent_topic_thread_ids.split('/')))

    def get_rent_topic_prices(self):
        prices_list = self.rent_topic_prices.split('/')
        return [list(map(int, s.strip('[]').replace('_', '').split(', '))) for s in prices_list]

    def make_forum_topics_data(self):
        thread_ids = self.get_rent_topic_thread_ids()
        prices = self.get_rent_topic_prices()
        return dict(zip(thread_ids, prices))


