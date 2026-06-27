from infrastructure.database.models import Advertisement


def _get_new_price_if_exists(advertisement: Advertisement):
    if advertisement.operation_type.value == "Аренда":
        return (
            f"\n                  {advertisement.price}"
            if advertisement.new_price
            else ""
        )
    return f"\n           {advertisement.price}" if advertisement.new_price else ""


def advertisement_reminder_message(reminder_time):
    return f"Уведомление для проверки актуальности данного объявления будет отправлено в <b>{reminder_time}</b>"


def rent_channel_advertisement_message(advertisement: Advertisement):
    new_price = _get_new_price_if_exists(advertisement)
    old_price = (
        f"{advertisement.old_price}"
        if not advertisement.new_price
        else f"<s>{advertisement.old_price}</s>"
    )

    return f"""
🔹{advertisement.name}

🔹Адрес: {advertisement.district.name} {advertisement.address}
🔹Комнат - {advertisement.rooms_quantity}
🔹Этаж - {advertisement.floor_from} из {advertisement.floor_to}
🔹Площадь - {advertisement.quadrature} м2

🔹Описание - {advertisement.repair_type.value}
{advertisement.description}

ID: {advertisement.unique_id}

🔹Цена - {old_price}{new_price}

Комиссия агентства - 50%

@{advertisement.user.tg_username}
{advertisement.user.phone_number} {advertisement.user.first_name}

🔽Наш удобный сайт🔽

<a href='https://tr.ee/vitrina'>🔘НАЙТИ КВАРТИРУ🔘</a>
"""


def buy_channel_advertisement_message(
    advertisement: Advertisement, installment_plan: str | None = None
):
    plan_text = "\nМожно в "
    if installment_plan == "full":
        plan_text += "Ипотеку\n"
    elif installment_plan == "partial":
        plan_text += "Частичная ипотека\n"
    elif installment_plan == "no" or installment_plan is None:
        plan_text = ""

    house_quadrature = (
        f"Общая площадь - {advertisement.house_quadrature_from} кв.м"
        if advertisement.category.slug == "doma"
        else ""
    )

    new_price = _get_new_price_if_exists(advertisement)
    old_price = (
        f"{advertisement.old_price}"
        if not advertisement.new_price
        else f"<s>{advertisement.old_price}</s>"
    )
    return f"""
{advertisement.name}

Адрес: {advertisement.district.name} {advertisement.address} 

Комнат - {advertisement.rooms_quantity} / Площадь - {advertisement.quadrature} кв.м
Этаж - {advertisement.floor_from} / Этажность - {advertisement.floor_to}
{house_quadrature}

Описание - {advertisement.repair_type.value}
{advertisement.description}

ID: {advertisement.unique_id}

Цена: {old_price}{new_price}
{plan_text}
Подробности по телефону: {advertisement.user.phone_number} {advertisement.user.first_name}
@{advertisement.user.tg_username}

🔽Наш удобный сайт🔽

<a href='https://tr.ee/vitrina'>🔘НАЙТИ КВАРТИРУ🔘</a>
"""
