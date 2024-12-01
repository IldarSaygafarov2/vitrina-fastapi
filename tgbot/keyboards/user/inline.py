from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.database.models import Advertisement, Category, District


def realtor_start_kb(realtor_chat_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="Создать объявление", callback_data=f"create_advertisement")
    kb.button(
        text="Мои объявления",
        callback_data=f"show_realtors_advertisement:{realtor_chat_id}",
    )
    return kb.as_markup()


def operation_type_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Покупка", callback_data="operation_type:buy")
    kb.button(text="Аренда", callback_data="operation_type:rent")

    return kb.as_markup()


def categories_kb(categories: list["Category"]):
    kb = InlineKeyboardBuilder()

    for category in categories:
        kb.button(text=category.name, callback_data=f"chosen_category:{category.id}")

    kb.adjust(2)
    return kb.as_markup()


def districts_kb(districts: list["District"]):
    kb = InlineKeyboardBuilder()
    for district in districts:
        kb.button(text=district.name, callback_data=f"chosen_district:{district.id}")

    kb.adjust(1)
    return kb.as_markup()


def property_type_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Новостройка", callback_data=f"property_type:new")
    kb.button(text="Вторичный фонд", callback_data=f"property_type:old")
    return kb.as_markup()


def is_studio_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="is_studio:yes")
    kb.button(text="Нет", callback_data="is_studio:no")
    return kb.as_markup()


def repair_type_kb(repair_types: dict):
    kb = InlineKeyboardBuilder()
    for key, value in repair_types.items():
        kb.button(text=value, callback_data=f"repair_type:{key}")
    kb.adjust(2)
    return kb.as_markup()


def realtor_advertisements_kb(
    advertisements: list["Advertisement"],
    for_admin: bool = False,
):
    kb = InlineKeyboardBuilder()
    for idx, advertisement in enumerate(advertisements, start=1):
        callback = (
            f"realtor_advertisement:{advertisement.id}"
            if not for_admin
            else f"rg_realtor_advertisement:{advertisement.id}"
        )
        kb.button(
            text=f"{idx}. {advertisement.name}",
            callback_data=callback,
        )
    kb.button(text="На главную", callback_data="return_home")
    kb.adjust(1)
    return kb.as_markup()


def return_home_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="На главную", callback_data="return_home")
    return kb.as_markup()


def advertisement_actions_kb(advertisement_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="Изменить", callback_data=f"advertisement_update:{advertisement_id}")
    kb.button(text="Удалить", callback_data=f"advertisement_delete:{advertisement_id}")
    kb.button(text="На главную", callback_data="return_home")
    kb.adjust(2)
    return kb.as_markup()
