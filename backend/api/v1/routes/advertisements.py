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
    count = advertisements["total_count"]

    advertisements = [
        AdvertisementDTO.model_validate(obj, from_attributes=True)
        for obj in advertisements["data"]
    ]

    return PaginatedAdvertisementDTO(
        total=count,
        limit=filters.limit,
        offset=filters.offset,
        results=advertisements,
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

    related_objects = await repo.advertisements.get_advertisements_by_category_id(
        category_id=advertisement.category.id,
    )

    # advertisement.related_objects = [
    #     AdvertisementDTO.model_validate(obj, from_attributes=True)
    #     for obj in related_objects
    # ]

    advertisement.related_objects = related_objects

    advertisement.images = sorted(
        [i.model_dump() for i in advertisement.images],
        key=lambda l: l["id"],
    )

    if advertisement is None:
        return {"detail": "Advertisement not found"}

    return advertisement
