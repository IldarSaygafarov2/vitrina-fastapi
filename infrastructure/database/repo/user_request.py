from sqlalchemy import insert

from infrastructure.database.models import UserRequest
from .base import BaseRepo


class UserRequestRepo(BaseRepo):
    async def create(
            self,
            first_name: str,
            operation_type: str,
            object_type: str,
            phone_number: str,
            message: str
    ):
        stmt = (
            insert(UserRequest)
            .values(
                first_name=first_name,
                operation_type=operation_type,
                object_type=object_type,
                phone_number=phone_number,
                message=message
            )
            .returning(UserRequest)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()
