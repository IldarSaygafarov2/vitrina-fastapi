from aiogram import Router
from tgbot.filters.role import RoleFilter


router = Router()
router.message.filter(RoleFilter(role='group_director'))


