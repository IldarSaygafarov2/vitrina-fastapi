from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from tgbot.filters.role import RoleFilter
from tgbot.keyboards.admin.inline import admin_start_kb

router = Router()
router.message.filter(RoleFilter(role='group_director'))


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f'''Привет, руководитель группы

Выберите действие снизу    
    ''', reply_markup=admin_start_kb())
