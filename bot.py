import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

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


async def main():
    setup_logging()

    config = load_config(".env")
    storage = MemoryStorage()
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML, link_preview_is_disabled=True
        ),
    )

    bot_me = await bot.get_me()
    bot_id = bot_me.id
    is_member = await check_bot_membership(bot, config.super_group.rent_supergroup_id, bot_id)
    if is_member:
        print("Bot is a member of the supergroup.")
    else:
        print("Bot is NOT a member of the supergroup.")


    dp = Dispatcher(storage=storage)
    dp["config"] = config

    dp.include_routers(*routers_list)

    engine = create_engine(db=config.db)
    session_pool = create_session_pool(engine=engine)

    register_global_middlewares(dp, config, session_pool)

    await dp.start_polling(bot)

async def check_bot_membership(bot: Bot, chat_id: str, bot_user_id: int):
    try:
        member = await bot.get_chat_member(chat_id, bot_user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking bot membership: {e}")
        return False

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot was stopped")
