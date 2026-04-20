import re

from aiogram import Router, types

from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool

config = load_config(".env")

channel_router = Router()

# database connection
engine = create_engine(config.db)
session = create_session_pool(engine)


@channel_router.channel_post()
async def react_to_channel_posted_message(message: types.Message):

    async with session() as _session:
        repo = RequestsRepo(_session)

    caption = message.caption

    message_id = message.message_id
    unique_id = re.search(r"ID: \d+", caption)
    if unique_id is not None:
        unique_id = unique_id.group()
        unique_id = "".join(list(filter(str.isdigit, unique_id)))

    await repo.channel_messages.add_channel_message(
        message_id=message_id,
        unique_id=unique_id,
        channel_name=message.chat.username,
    )
    print(f"added new channel message: {message_id=}, {unique_id=}")
    await _session.close()


# TODO: создать таблицу для сообщений канала
# TODO: добавлять в эту таблицу данные при отправке сообщений в канал
# TODO: написать селери задачу которая будет раз в час проверять добавленные значения в таблицу и если поле unique_id дублируется, то удалять сообщений дубликатов
