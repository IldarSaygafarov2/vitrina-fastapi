from fastapi import APIRouter

from backend.app.config import config
from backend.app.dependencies import get_repo
from infrastructure.database.repo.requests import RequestsRepo
from typing import Annotated
from backend.core.interfaces.user import UserCreateDTO


router = APIRouter(
    prefix=config.api_prefix.v1.users,
    tags=["Users"],
)


@router.get("/")
async def get_users():
    return []
