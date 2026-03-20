import os
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from backend.app.config import config
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.role import RoleFilter
from tgbot.keyboards.admin.inline import advertisement_moderation_kb
from tgbot.keyboards.user.inline import is_advertisement_actual_kb, is_price_actual_kb
from tgbot.misc.user_states import AdvertisementRelevanceState
from tgbot.templates.messages import advertisement_reminder_message
from tgbot.utils import helpers

router = Router()
router.message.filter(RoleFilter(role="realtor"))
router.callback_query.filter(RoleFilter(role="realtor"))


@router.callback_query(F.data.startswith("check_actual"))
async def handle_check_actual(callback: CallbackQuery):
    """Сначала спрашиваем, актуально ли объявление."""
    await callback.answer()
    advertisement_id = int(callback.data.split(":")[-1])
    await callback.message.edit_text(
        text="Данное объявление актуально?",
        reply_markup=is_advertisement_actual_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("actual"))
async def react_to_advertisement_actual(call: CallbackQuery):
    """Если объявление актуально — уточняем, изменилась ли цена."""
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    await call.message.edit_text(
        text="Изменилась ли цена данного объявления?",
        reply_markup=is_price_actual_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("not_actual"))
async def react_to_advertisement_not_actual(
    call: CallbackQuery,
    repo: RequestsRepo,
):
    """Если объявление неактуально — удаляем объявление и его фото из БД и файловой системы."""
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    if not advertisement:
        await call.message.edit_text("Объявление уже удалено.")
        return

    agent = await repo.users.get_user_by_id(advertisement.user_id)
    director_chat_id = agent.added_by if agent else None
    adv_name = advertisement.name
    adv_uid = advertisement.unique_id

    # Удаляем файлы изображений
    for image in advertisement.images:
        if image.url and os.path.exists(image.url):
            try:
                os.remove(image.url)
            except OSError:
                pass

    # Удаляем превью, если существует
    if advertisement.preview and os.path.exists(advertisement.preview):
        try:
            os.remove(advertisement.preview)
        except OSError:
            pass

    # Удаляем объявление (изображения и очередь удаляются каскадно в БД)
    await repo.advertisements.delete_advertisement(advertisement_id)

    if director_chat_id:
        agent_name = agent.fullname or f"{agent.first_name} {agent.lastname}"
        try:
            await call.bot.send_message(
                director_chat_id,
                f"Агент <i>{agent_name}</i> отметил объявление как неактуальное. "
                f"Оно удалено из базы.\n"
                f"Название: <b>{adv_name}</b>\n"
                f"ID: <code>{adv_uid}</code>",
                parse_mode="HTML",
            )
        except Exception as e:
            await call.bot.send_message(
                chat_id=config.tg_bot.test_main_chat_id,
                text=f"Не удалось уведомить руководителя об удалении объявления: {e}",
            )

    await call.message.edit_text("Объявление помечено как неактуальное и полностью удалено.")


@router.callback_query(F.data.startswith("price_changed"))
async def react_to_advertisement_price_changed(
    call: CallbackQuery, state: FSMContext
):
    """Если цена объявления поменялась — запрашиваем новую цену."""
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    await state.set_state(AdvertisementRelevanceState.new_price)
    await state.update_data(advertisement_id=advertisement_id)
    await call.message.edit_text(
        "Напишите новую цену для объявления",
        reply_markup=None,
    )


@router.message(AdvertisementRelevanceState.new_price, F.text)
async def set_actual_price_for_advertisement(
    message: Message, repo: RequestsRepo, state: FSMContext
):
    """Записываем новую цену и отправляем объявление руководителю на модерацию."""
    state_data = await state.get_data()
    chat_id = message.chat.id
    advertisement_id = state_data.get("advertisement_id")

    user = await repo.users.get_user_by_chat_id(chat_id)
    director_chat_id = user.added_by
    if not director_chat_id:
        await message.answer("Ошибка: руководитель не найден.")
        await state.clear()
        return

    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id
    )
    if not advertisement:
        await message.answer("Объявление не найдено.")
        await state.clear()
        return

    operation_type = advertisement.operation_type.value
    reminder_delta = config.reminder_config.get_reminder_timedelta(
        operation_type
    )
    next_reminder_date = (
        datetime.now() + reminder_delta
    ).date()

    new_price_str = helpers.filter_digits(message.text)
    if not new_price_str:
        await message.answer("Введите корректную цену (только цифры).")
        return

    new_price = int(new_price_str)

    await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        old_price=advertisement.price,
        price=new_price,
        new_price=new_price,
        is_moderated=False,
        reminder_time=next_reminder_date,
    )

    updated_advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id
    )
    media_group = await helpers.collect_media_group_for_advertisement(
        updated_advertisement, repo
    )

    await message.answer("Объявление отправлено руководителю на проверку")
    agent_fullname = user.fullname or f"{user.first_name} {user.lastname}"

    await message.bot.send_media_group(director_chat_id, media=media_group)
    await message.bot.send_message(
        director_chat_id,
        f"""
Агент: <i>{agent_fullname}</i> обновил объявление
Новая цена объявления: <b>{new_price}</b>
Объявление прошло модерацию?
""",
        parse_mode="HTML",
        reply_markup=advertisement_moderation_kb(advertisement_id=advertisement_id),
    )
    await state.clear()


@router.callback_query(F.data.startswith("price_not_changed"))
async def react_to_advertisement_price_not_changed(
    call: CallbackQuery,
    repo: RequestsRepo,
):
    """Если цена не изменилась — отправляем объявление в группу Аренда или Продажа."""
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id
    )
    if not advertisement:
        await call.message.answer("Объявление не найдено.")
        return

    operation_type = advertisement.operation_type.value
    reminder_delta = config.reminder_config.get_reminder_timedelta(
        operation_type
    )
    next_reminder_date = (
        datetime.now() + reminder_delta
    ).date()

    advertisement_photos = await helpers.get_advertisement_photos(
        advertisement_id, repo
    )
    channel_name, advertisement_message = (
        helpers.get_channel_name_and_message_by_operation_type(advertisement)
    )
    media_group = helpers.get_media_group(
        advertisement_photos, advertisement_message
    )

    await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        reminder_time=next_reminder_date,
    )

    await helpers.send_message_to_rent_topic(
        bot=call.bot,
        price=advertisement.price,
        operation_type=operation_type,
        media_group=media_group,
    )

    if operation_type == "Покупка":
        try:
            await call.bot.send_media_group(
                chat_id=config.tg_bot.base_channel_name,
                media=media_group,
            )
        except Exception as e:
            await call.bot.send_message(
                chat_id=config.tg_bot.test_main_chat_id,
                text=f"Ошибка при отправке в базовый канал: {e}",
            )

    try:
        await call.bot.send_media_group(
            chat_id=channel_name,
            media=media_group,
        )
    except Exception as e:
        await call.bot.send_message(
            chat_id=config.tg_bot.test_main_chat_id,
            text=f"Ошибка при отправке медиа группы: {e}",
        )

    formatted_reminder_time = next_reminder_date.strftime("%Y-%m-%d")
    agent = await repo.users.get_user_by_id(advertisement.user_id)

    await call.message.edit_text(
        f"Объявление отправлено в группу.\n"
        f"Следующая проверка актуальности: <b>{formatted_reminder_time}</b>",
        parse_mode="HTML",
    )
    if agent.tg_chat_id:
        await call.bot.send_message(
            agent.tg_chat_id,
            text=advertisement_reminder_message(formatted_reminder_time),
            parse_mode="HTML",
        )
