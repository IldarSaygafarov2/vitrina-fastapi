from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from .advertisement import AdvertisementRepo, AdvertisementImageRepo
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

    @property
    def advertisements(self) -> AdvertisementRepo:
        return AdvertisementRepo(self.session)

    @property
    def advertisement_images(self) -> AdvertisementImageRepo:
        return AdvertisementImageRepo(self.session)
