from .admin.menu import router as admin_router
from .common.start import router as common_user_router
from .realtor.menu import router as realtor_router
from .realtor.states import router as realtor_states_router

routers_list = [
    admin_router,
    common_user_router,
    realtor_router,
    realtor_states_router,
]


__all__ = [
    "routers_list",
]
