import asyncio
import uuid

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from config.loader import load_config
from external.db_migrate import clean_json
from infrastructure.database.models.advertisement import (
    Advertisement,
    AdvertisementImage,
)
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool


async def add_advertisements(session: AsyncSession):
    advertisements = clean_json("external/advertisements.json")

    repo = RequestsRepo(session)

    result = []
    result_images = []

    for adv in advertisements:
        slug = f'{slugify(adv["name"])}-{uuid.uuid4()}'[:30]

        category_id = await repo.categories.get_category_id_by_name(
            category_name=adv["category_id"]
        )
        district_id = await repo.districts.get_district_id_by_name(
            district_name=adv["district_id"]
        )

        user_id = await repo.users.get_user_by_username(username=adv["user_id"])

        obj = Advertisement(
            name=adv["name"],
            name_uz=adv["name_uz"],
            description=adv["description"],
            description_uz=adv["description_uz"],
            address=adv["address"],
            address_uz=adv["address_uz"],
            operation_type=adv["operation_type"].upper(),
            operation_type_uz=adv["operation_type"].upper(),
            property_type=adv["property_type"].upper(),
            property_type_uz=adv["property_type"].upper(),
            repair_type=adv["repair_type"].upper(),
            repair_type_uz=adv["repair_type"].upper(),
            price=int(adv["price"]),
            rooms_qty_from=int(adv["rooms_qty_from"]),
            rooms_qty_to=int(adv["rooms_qty_to"]),
            quadrature_from=int(adv["quadrature_from"]),
            quadrature_to=int(adv["quadrature_to"]),
            floor_from=int(adv["floor_from"]),
            floor_to=int(adv["floor_to"]),
            is_studio=bool(adv["is_studio"]),
            category_id=category_id,
            district_id=district_id,
            house_quadrature_to=(
                int(adv["house_quadrature_to"]) if adv["house_quadrature_to"] else 0
            ),
            house_quadrature_from=(
                int(adv["house_quadrature_from"]) if adv["house_quadrature_from"] else 0
            ),
            slug=slug,
            user_id=user_id.id,
        )
        # for image in adv["images"]:
        #     img_obj = AdvertisementImage(advertisement_id=obj.id, url=image["photo"])
        #     result_images.append(img_obj)
        result.append(obj)

    session.add_all(result)
    await session.commit()


async def main():
    config = load_config(".env")
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine=engine)

    async with session_pool() as session:
        await add_advertisements(session=session)


asyncio.run(main())
