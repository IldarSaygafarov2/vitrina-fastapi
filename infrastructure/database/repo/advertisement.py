from sqlalchemy import insert, select, update

from infrastructure.database.models import Advertisement, AdvertisementImage
from infrastructure.utils.slugifier import generate_slug
from .base import BaseRepo


class AdvertisementRepo(BaseRepo):

    async def create_advertisement(
        self,
        category: int,
        district: int,
        title: str,
        description: str,
        address: str,
        creation_year: int,
        price: int,
        is_studio: bool,
        rooms_from: int,
        rooms_to: int,
        quadrature_from: int,
        quadrature_to: int,
        floor_from: int,
        floor_to: int,
        house_quadrature_from: int,
        house_quadrature_to: int,
        user: int,
        operation_type,
        property_type,
        repair_type,
    ):
        slug = generate_slug(title)
        stmt = (
            insert(Advertisement)
            .values(
                slug=slug,
                operation_type=operation_type,
                category=category,
                district=district,
                name=title,
                description=description,
                address=address,
                property_type=property_type,
                creation_year=creation_year,
                price=price,
                is_studio=is_studio,
                rooms_qty_from=rooms_from,
                rooms_qty_to=rooms_to,
                quadrature_from=quadrature_from,
                quadrature_to=quadrature_to,
                floor_from=floor_from,
                floor_to=floor_to,
                house_quadrature_from=house_quadrature_from,
                house_quadrature_to=house_quadrature_to,
                user=user,
                repair_type=repair_type,
            )
            .returning(Advertisement)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_advertisements(self):
        stmt = select(Advertisement)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_advertisement_by_slug(self, advertisement_slug: str):
        stmt = select(Advertisement).where(Advertisement.slug == advertisement_slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_advertisement_by_id(self, advertisement_id: int):
        stmt = select(Advertisement).where(Advertisement.id == advertisement_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_advertisement_by_title(self, title: str):
        stmt = select(Advertisement).where(Advertisement.name == title)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class AdvertisementImageRepo(BaseRepo):
    async def insert_advertisement_image(
        self,
        advertisement_id: int,
        url: str,
    ):
        stmt = insert(AdvertisementImage).values(
            advertisement_id=advertisement_id,
            url=url,
        )
        await self.session.execute(stmt)
        await self.session.commit()
