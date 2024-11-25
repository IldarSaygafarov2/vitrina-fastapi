from typing import TYPE_CHECKING
from aiogram import Router
from aiogram.types import Message
from tgbot.filters.realtor import RealtorFilter

from aiogram.filters import CommandStart

router = Router()
router.message.filter(RealtorFilter())

from infrastructure.database.repo.requests import RequestsRepo


@router.message(CommandStart())
async def start(message: Message, repo: RequestsRepo):
    username = message.from_user.username
    user = await repo.users.get_user_role(tg_username=username)
    print(user)
    await message.answer("hello realtor")
