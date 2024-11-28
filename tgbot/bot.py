import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.loader import Config, load_config
from infrastructure.database.setup import create_engine, create_session_pool
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.database import DatabaseMiddleware


def setup_logging():
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def register_global_middlewares(dp: Dispatcher, config: Config, session_pool=None):
    middleware_types = [
        ConfigMiddleware(config),
        DatabaseMiddleware(session_pool),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


config = load_config(".env")
engine = create_engine(db=config.db)
session_pool = create_session_pool(engine=engine)

bot = Bot(
    token=config.tg_bot.token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML, link_preview_is_disabled=True
    ),
)
dp = Dispatcher()
dp["config"] = config
dp.include_routers(*routers_list)


register_global_middlewares(dp, config, session_pool)
setup_logging()
