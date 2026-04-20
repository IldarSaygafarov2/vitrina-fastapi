from .admin.add_realtor import router as add_realtor_router
from .admin.menu import router as admin_router
from .admin.update_realtor import router as update_realtor_router
from .channel.text import channel_router
from .common.menu import router as common_menu_router
from .common.start import router as common_user_router
from .realtor.advertisement_actual import router as realtor_actual_router
from .realtor.advertisement_update import router as update_router
from .realtor.menu import router as realtor_router
from .realtor.states import router as realtor_states_router

# from .dev.menu import dev_router

routers_list = [
    # group director routers
    admin_router,
    add_realtor_router,
    update_realtor_router,
    common_user_router,
    # realtor routers
    realtor_router,
    realtor_states_router,
    realtor_actual_router,
    common_menu_router,
    update_router,
    # channel router
    channel_router,
]


__all__ = [
    "routers_list",
]
