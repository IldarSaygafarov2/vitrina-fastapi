from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from .category import CategoryRepo
from .district import DistrictRepo


@dataclass
class RequestsRepo:
    session: AsyncSession

    @property
    def categories(self) -> CategoryRepo:
        return CategoryRepo(self.session)

    @property
    def districts(self) -> DistrictRepo:
        return DistrictRepo(self.session)
