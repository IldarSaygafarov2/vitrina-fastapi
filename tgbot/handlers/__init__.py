from .common.start import router as common_user_router
from .realtor.menu import router as realtor_router

routers_list = [
    common_user_router,
    realtor_router,
]


__all__ = [
    "routers_list",
]
