import sqlalchemy as sa

from infrastructure.database.models.channel_message import ChannelMessage

from .base import BaseRepo


class ChannelMessageRepo(BaseRepo):
    async def add_channel_message(
        self, message_id: int, unique_id: str, channel_name: str | None = None
    ):
        stmt = sa.insert(ChannelMessage).values(
            message_id=message_id,
            unique_id=unique_id,
            channel_name=channel_name,
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_channel_message(self, message_id: int, unique_id: str):
        stmt = sa.select(ChannelMessage).where(
            ChannelMessage.message_id == message_id,
            ChannelMessage.unique_id == unique_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_channel_messages(self):
        stmt = sa.select(ChannelMessage)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_channel_message(self, message_id: int):
        stmt = sa.delete(ChannelMessage).where(ChannelMessage.message_id == message_id)
        await self.session.execute(stmt)
        await self.session.commit()
