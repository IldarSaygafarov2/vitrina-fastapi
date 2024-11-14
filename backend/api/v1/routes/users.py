from fastapi import APIRouter

from backend.app.config import config


router = APIRouter(
    prefix=config.api_prefix.v1.users,
    tags=['Users']
)


@router.get('/')
async def get_users():
    return []
