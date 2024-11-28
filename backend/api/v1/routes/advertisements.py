from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.config import config
from backend.app.dependencies import get_repo
from infrastructure.database.repo.requests import RequestsRepo
from backend.core.interfaces.advertisement import (
    AdvertisementDetailDTO,
    AdvertisementDTO,
)


router = APIRouter(
    prefix=config.api_prefix.v1.advertisements,
    tags=["Advertisements"],
)


@router.get("/")
async def get_advertisements(
    repo: Annotated[RequestsRepo, Depends(get_repo)],
) -> list[AdvertisementDTO]:
    advertisements = await repo.advertisements.get_advertisements()
    return advertisements


@router.get("/{advertisement_id}")
async def get_advertisement(
    advertisement_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):

    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )
    return AdvertisementDetailDTO.model_validate(advertisement, from_attributes=True)
