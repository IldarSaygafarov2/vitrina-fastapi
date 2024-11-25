from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from .category import CategoryRepo
from .district import DistrictRepo
from .user import UserRepo


@dataclass
class RequestsRepo:
    session: AsyncSession

    @property
    def categories(self) -> CategoryRepo:
        return CategoryRepo(self.session)

    @property
    def districts(self) -> DistrictRepo:
        return DistrictRepo(self.session)

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)
