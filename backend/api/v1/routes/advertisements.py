from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.app.config import config
from backend.app.dependencies import get_repo
from backend.core.interfaces.advertisement import (
    AdvertisementDetailDTO,
    AdvertisementDTO,
    PaginatedAdvertisementDTO
)
from infrastructure.database.repo.requests import RequestsRepo
from backend.core.filters.advertisement import AdvertisementFilter

router = APIRouter(
    prefix=config.api_prefix.v1.advertisements,
    tags=["Advertisements"],
)


@router.get("/")
async def get_advertisements(
        filters: Annotated[AdvertisementFilter, Query()],
        repo: Annotated[RequestsRepo, Depends(get_repo)],
) -> PaginatedAdvertisementDTO:

    advertisements = await repo.advertisements.get_advertisements(
        limit=filters.limit,
        offset=filters.offset
    )
    advertisements = [AdvertisementDTO.model_validate(obj, from_attributes=True) for obj in advertisements]

    total = await repo.advertisements.get_total_advertisements()

    return PaginatedAdvertisementDTO(
        total=total,
        limit=filters.limit,
        offset=filters.offset,
        results=advertisements
    )



@router.get("/{advertisement_id}")
async def get_advertisement(
    advertisement_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):

    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )

    if advertisement is None:
        return {"detail": "Advertisement not found"}
    return AdvertisementDetailDTO.model_validate(advertisement, from_attributes=True)
