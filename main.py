import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api import router as api_router
from backend.app.config import config

main_app = FastAPI(debug=True)
main_app.include_router(api_router)

main_app.mount("/media", StaticFiles(directory="media"), name="media")


main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=config.run_api.api_host,
        port=config.run_api.api_port,
        reload=False,
    )

# import uvicorn
# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.types import Update

# from backend.api import router as api_router
# from backend.app.config import config
# from config.loader import load_config
# from infrastructure.database.setup import create_engine, create_session_pool
# from tgbot.handlers import routers_list
# from tgbot.middlewares.config import ConfigMiddleware
# from tgbot.middlewares.database import DatabaseMiddleware

# tg_config = load_config(".env")


# from contextlib import asynccontextmanager


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Создаём всё внутри lifespan — не на уровне модуля
#     tg_config = load_config(".env")

#     bot = Bot(
#         token=tg_config.tg_bot.token,
#         default=DefaultBotProperties(
#             parse_mode=ParseMode.HTML, link_preview_is_disabled=True
#         ),
#     )

#     dp = Dispatcher(storage=MemoryStorage())
#     dp["config"] = tg_config
#     dp.include_routers(*routers_list)

#     engine = create_engine(db=tg_config.db)
#     session_pool = create_session_pool(engine=engine)

#     for middleware in [ConfigMiddleware(tg_config), DatabaseMiddleware(session_pool)]:
#         dp.message.outer_middleware(middleware)
#         dp.callback_query.outer_middleware(middleware)

#     await bot.set_webhook(f"{tg_config.tg_bot.webhook_url}/webhook")

#     app.state.bot = bot
#     app.state.dp = dp

#     yield

#     await bot.delete_webhook()
#     await bot.session.close()


# main_app = FastAPI(debug=True, lifespan=lifespan)


# main_app.include_router(api_router)
# main_app.mount("/media", StaticFiles(directory="media"), name="media")

# main_app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @main_app.post("/webhook")
# async def webhook(request: Request):
#     data = await request.json()
#     update = Update(**data)
#     await request.app.state.dp.feed_update(request.app.state.bot, update)
#     return {"ok": True}


# if __name__ == "__main__":
#     uvicorn.run(
#         "main:main_app",
#         host=config.run_api.api_host,
#         port=config.run_api.api_port,
#         reload=False,
#     )
