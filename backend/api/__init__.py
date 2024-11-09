from backend.api.v1 import router as api_v1_router

from fastapi import APIRouter


router = APIRouter()
router.include_router(api_v1_router)
