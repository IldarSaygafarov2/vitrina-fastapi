from fastapi import APIRouter
from backend.app.config import config

from .routes.districts import router as districts_router
from .routes.categories import router as categories_router
from .routes.advertisements import router as advertisements_router
from .routes.users import router as users_router

router = APIRouter(
    prefix=config.api_prefix.v1.prefix
)


router.include_router(districts_router)
router.include_router(categories_router)
router.include_router(advertisements_router)
router.include_router(users_router)