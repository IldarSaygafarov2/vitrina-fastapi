from aiogram import Router, types, F
from aiogram.filters.command import Command

from backend.app.config import config
from pprint import pprint

router = Router()


@router.message(Command(commands=['test']), F.chat.type.in_({"supergroup"}))
async def test_send_message_to_topic(message: types.Message):
    pprint(message.model_dump())
    print(message.reply_to_message.forum_topic_created)
