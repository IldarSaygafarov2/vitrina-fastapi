from infrastructure.database.models import Advertisement


def rent_channel_advertisement_message(advertisement: Advertisement):
    return f"""
🔹Аренда 🔹


🔹Адрес: {advertisement.address}
🔹Комнат - {advertisement.rooms_quantity}
🔹Этаж - {advertisement.floor_from} из {advertisement.floor_to}
🔹Площадь - {advertisement.quadrature} м2


🔹Описание - {advertisement.repair_type.value}
{advertisement.description}

ID: {advertisement.unique_id}

🔹Цена - {advertisement.price}$

@{advertisement.user.tg_username}
{advertisement.user.phone_number} {advertisement.user.first_name}

А если вы хотите купить квартиру, переходите в канал с Продажей 👇
@ivitrinauz

"""


def buy_channel_advertisement_message(advertisement: Advertisement):
    return f"""
{advertisement.name}

Адрес: {advertisement.district.name} {advertisement.address} 

Комнат - {advertisement.rooms_quantity} / Площадь - {advertisement.quadrature} кв.м
Этаж - {advertisement.floor_from} / Этажность - {advertisement.floor_to}

Описание - {advertisement.repair_type.value}
{advertisement.description}

ID: {advertisement.unique_id}

Цена: {advertisement.price}$

Подробности по телефону: {advertisement.user.phone_number} {advertisement.user.first_name}
@{advertisement.user.tg_username}

<a href='https://t.me/ivitrinauz'>📱 ПРОДАЖА НЕДВИЖИМОСТИ</a>

<a href='https://t.me/vitrinanedvizhimosti'>📱 АРЕНДА НЕДВИЖИМОСТИ</a>

<a href='https://www.instagram.com/vitrina.uz?igsh=d3J6emEyeGE3N3V6'>📱  НАШ Instagram</a>
"""
