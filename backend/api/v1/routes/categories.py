from fastapi import APIRouter

from backend.app.config import config


router = APIRouter(
    prefix=config.api_prefix.v1.categories,
    tags=['Categories']
)


@router.get('/')
async def get_categories():
    return []


@router.get('/{id}')
async def get_category(category_id: int):
    return {}
