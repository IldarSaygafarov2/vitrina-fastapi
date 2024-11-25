from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import Message
from infrastructure.database.setup import create_engine, create_session_pool

from infrastructure.database.repo.requests import RequestsRepo

from config.loader import load_config

config = load_config(".env")
engine = create_engine(config.db)
session_pool = create_session_pool(engine)


class RealtorFilter(BaseFilter):
    required_role: str = "realtor"

    async def __call__(self, message: Message) -> bool:
        username = message.from_user.username

        async with session_pool() as session:
            repo = RequestsRepo(session)

            user_role = await repo.users.get_user_role(tg_username=username)
            if not user_role:
                return False

            return user_role.value == self.required_role
