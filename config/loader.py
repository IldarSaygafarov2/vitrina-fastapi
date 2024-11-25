from dataclasses import dataclass
from typing import Optional

from environs import Env

from config.api_config import ApiPrefix, RunConfig
from config.db_config import DbConfig
from config.tg_config import TgBot
from config.webhook_config import WebhookConfig


@dataclass
class Config:
    db: DbConfig
    api_prefix: ApiPrefix
    run_api: RunConfig
    tg_bot: TgBot
    webhook: WebhookConfig


def load_config(path: Optional[str] = None) -> "Config":
    env = Env()
    env.read_env(path)

    db_config = DbConfig.from_env(env)
    run_api_config = RunConfig.from_env(env)
    tg_bot = TgBot.from_env(env)
    webhook = WebhookConfig.from_env(env)
    api_prefix = ApiPrefix()

    return Config(
        db=db_config,
        api_prefix=api_prefix,
        run_api=run_api_config,
        tg_bot=tg_bot,
        webhook=webhook,
    )
