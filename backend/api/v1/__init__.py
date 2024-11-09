from fastapi import APIRouter

from .routes.districts import router as districts_router


router = APIRouter()


router.include_router(districts_router)
