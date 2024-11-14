from fastapi import APIRouter

from backend.app.config import config


router = APIRouter(
    prefix=config.api_prefix.v1.advertisements,
    tags=['Advertisements']
)


@router.get('/')
async def get_advertisements():
    return []


@router.get('/{id}')
async def get_advertisement(advertisement_id: int):
    return {}


@router.get('/{id}/gallery')
async def get_advertisement_gallery(advertisement_id: int):
    return []
