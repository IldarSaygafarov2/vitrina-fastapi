from fastapi import APIRouter
from backend.app.config import config

router = APIRouter(
    prefix=config.api_prefix.v1.districts,
    tags=['Districts']
)


@router.get('/')
async def get_districts():
    return []


@router.get('/{id}')
async def get_district(district_id: int):
    return {}


