from sqlalchemy import insert, select, update, delete

from infrastructure.database.models import User

from .base import BaseRepo


class UserRepo(BaseRepo):
    async def create_user(
        self,
        first_name: str,
        lastname: str,
        phone_number: str,
        tg_username: str,
        role: str,
    ):
        stmt = (
            insert(User)
            .values(
                first_name=first_name,
                lastname=lastname,
                phone_number=phone_number,
                tg_username=tg_username,
                role=role,
            )
            .returning(User)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def update_user_chat_id(self, tg_username: str, tg_chat_id: int):
        stmt = (
            update(User)
            .values(tg_chat_id=tg_chat_id)
            .where(User.tg_username == tg_username)
            .returning(User)
        )
        updated = await self.session.execute(stmt)
        await self.session.commit()
        return updated.scalar_one()

    async def get_user_role(self, tg_username: str):
        stmt = select(User.role).where(User.tg_username == tg_username)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_user_by_chat_id(self, tg_chat_id: int):
        stmt = select(User).where(User.tg_chat_id == tg_chat_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_user_by_username(self, username: str):
        stmt = select(User).where(User.tg_username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_realtors(self):
        stmt = select(User).where(User.role == "REALTOR")
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_by_id(self, user_id: int):
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete_user(self, user_id: int):
        stmt = delete(User).where(User.id == user_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_user(self, user_id: int, **data):
        stmt = update(User).values(**data).where(User.id == user_id).returning(User)
        updated = await self.session.execute(stmt)
        await self.session.commit()
        return updated.scalar_one()
