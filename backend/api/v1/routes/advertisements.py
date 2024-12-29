from pprint import pprint
from typing import Annotated, Union

from fastapi import APIRouter, Depends, Query, Request

from backend.app.config import config
from backend.app.dependencies import get_repo
from backend.core.filters.advertisement import AdvertisementFilter
from backend.core.interfaces.advertisement import (
    AdvertisementDetailDTO,
    AdvertisementDTO,
    PaginatedAdvertisementDTO,
)
from infrastructure.database.repo.requests import RequestsRepo

router = APIRouter(
    prefix=config.api_prefix.v1.advertisements,
    tags=["Advertisements"],
)


@router.get("/")
async def get_advertisements(
    filters: Annotated[AdvertisementFilter, Query()],
    repo: Annotated[RequestsRepo, Depends(get_repo)],
) -> PaginatedAdvertisementDTO:
    advertisements = await repo.advertisements.get_filtered_advertisements(filters)

    advertisements = [
        AdvertisementDTO.model_validate(obj, from_attributes=True)
        for obj in advertisements
    ]

    advertisements_rooms = [adv.get_rooms for adv in advertisements]
    temp = []
    if filters.rooms:
        rooms_list = [int(room) for room in filters.rooms.split(",")]

        for room in rooms_list:
            for i in advertisements_rooms:
                if room not in i[1]:
                    continue
                temp.append(i[0])

    total = await repo.advertisements.get_total_advertisements()

    return PaginatedAdvertisementDTO(
        total=total,
        limit=filters.limit,
        offset=filters.offset,
        results=advertisements if not filters.rooms else temp,
    )


@router.get("/{advertisement_id}")
async def get_advertisement(
    request: Request,
    advertisement_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
) -> Union[AdvertisementDetailDTO, dict]:

    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )
    advertisement = AdvertisementDetailDTO.model_validate(
        advertisement, from_attributes=True
    )

    images = []

    for image in advertisement.images:
        image.url = f"{request.base_url}{image.url}"
        images.append(image)

    advertisement.images = images

    if advertisement is None:
        return {"detail": "Advertisement not found"}

    return advertisement
