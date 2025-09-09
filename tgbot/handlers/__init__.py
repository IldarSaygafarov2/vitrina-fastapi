from .admin.menu import router as admin_router
from .admin.states import router as admin_states_router
from .common.menu import router as common_menu_router
from .common.start import router as common_user_router
from .realtor.advertisement_update import router as update_router
from .realtor.menu import router as realtor_router
from .realtor.states import router as realtor_states_router

routers_list = [
    admin_router,
    admin_states_router,
    common_user_router,
    realtor_router,
    realtor_states_router,
    common_menu_router,
    update_router,
]


__all__ = [
    "routers_list",
]
