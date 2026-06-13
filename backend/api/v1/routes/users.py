from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from backend.app.config import config
from backend.app.dependencies import get_repo
from backend.core.interfaces.advertisement import AdvertisementDTO
from backend.core.interfaces.user import UserDTO, UserLoginDTO, UserSessionDTO
from infrastructure.database.repo.requests import RequestsRepo
from backend.api.websockets.manager import manager

router = APIRouter(
    prefix=config.api_prefix.v1.users,
    tags=["Users"],
)


def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return
    return user


@router.get("/{user_id}/advertisements/")
async def get_user_advertisements(
    user_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
) -> list[AdvertisementDTO]:
    advertisements = await repo.advertisements.get_user_advertisements(user_id=user_id)
    return advertisements


@router.post("/login/")
async def get_user_by_telegram_username(
    request: Request,
    login_data: UserLoginDTO,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
) -> UserSessionDTO | None:
    user = await repo.users.get_user_by_username(login_data.tg_username)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    request.session["user"] = UserSessionDTO.model_validate(
        user, from_attributes=True
    ).model_dump()
    return user


@router.get("/me/")
async def get_me(user=Depends(get_current_user)) -> UserSessionDTO | None:
    return user


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Вышел из системы"}
