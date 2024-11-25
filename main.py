import logging

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from aiogram.types import Update
from backend.api import router as api_router
from config.loader import load_config
from tgbot.bot import bot, dp

config = load_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_url = config.webhook.main_webhook_url
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )
    logging.info("webhook set to " + webhook_url)
    yield
    await bot.delete_webhook()
    logging.info("webhook removed")


main_app = FastAPI(lifespan=lifespan)
main_app.include_router(api_router)


@main_app.post("/webhook")
async def webhook(request: Request):
    logging.info("received webhook request")
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    logging.info("update processed")


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
