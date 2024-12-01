from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_start_kb():
    kb = InlineKeyboardBuilder()

    kb.button(text='Риелторы', callback_data='rg_realtors')
    kb.button(text='Районы', callback_data='rg_districts')
    kb.button(text='Категории', callback_data='rg_categories')

    kb.adjust(1)
    return kb.as_markup()
