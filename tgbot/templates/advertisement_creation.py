from infrastructure.database.models import Advertisement


def choose_operation_type_text() -> str:
    return "Выберите тип операции для этого объявления"


def choose_category_text(operation_type: str) -> str:
    return f"""Выбранный тип операции: <b>{operation_type}</b>

Выберите категорию недвижимости: """


def choose_photos_quantity_text(category_name: str):
    return f"""Выбранная категория: <b>{category_name}</b>

Напишите сколько фотографий будет в данном объявлении:
"""


def choose_photos_text(photos_quantity: str):
    return f"""Количество фотографий для объявления: <b>{photos_quantity}</b>

Отправьте столько фотографий, сколько указали
"""


def get_title_text(lang: str = "ru"):
    if lang == "uz":
        return "Напишите название объявления на узбекском "
    return "Напишите название объявления"


def get_description_text(lang: str = "ru"):
    if lang == "uz":
        return "Напишите описание для объявления на узбекском языке"
    return "Напишите описание для объвления"


def get_district_text():
    return "Выберите район, в котором расположена недвижимость: "


def get_address_text(district_name: str, lang: str = "ru"):

    return f"""Выбранный район: <b>{district_name}</b>

Напишите точный адрес недвижимости:
"""


def get_address_text_uz():
    return "Напишите точный адрес на узбекском"


def get_propety_type_text():
    return "Выберите текст недвижимости:"


def creation_year_text(property_type: str):
    return f"""Выбранный тип недвижимости: <b>{property_type}</b>

Укажите год постройки недвижимости
"""


def price_text(property_type: str):
    return f"""Выбранный тип недвижимости: <b>{property_type}</b>

Укажите цену для данного объвления
"""


def is_studio_text():
    return "Недвижимость является студией ?"


def realtor_advertisement_completed_text(
    advertisement: "Advertisement",
    lang: str = "ru",
):
    rooms_from_to = f"<b>Кол-во комнат</b>  <i>{advertisement.rooms_quantity}</i>"
    creation_year = (
        f"\n<b>Год постройки: </b><i>{advertisement.creation_year}</i>"
        if advertisement.creation_year
        else ""
    )

    house_quadrature = (
        f"\n<b>Площадь участка: от </b>{advertisement.house_quadrature_from} до {advertisement.house_quadrature_to}"
        if advertisement.house_quadrature_from and advertisement.house_quadrature_to
        else ""
    )

    name = advertisement.name if lang == "ru" else advertisement.name_uz
    description = (
        advertisement.description if lang == "ru" else advertisement.description_uz
    )
    operation_type = (
        advertisement.operation_type.value
        if lang == "ru"
        else advertisement.operation_type_uz.value
    )
    district = (
        advertisement.district.name if lang == "ru" else advertisement.district.name_uz
    )
    category = (
        advertisement.category.name if lang == "ru" else advertisement.category.name_uz
    )
    address = advertisement.address if lang == "ru" else advertisement.address_uz
    property_type = (
        advertisement.property_type.value
        if lang == "ru"
        else advertisement.property_type_uz.value
    )
    repair_type = (
        advertisement.repair_type.value
        if lang == "ru"
        else advertisement.repair_type_uz.value
    )

    return f"""
<b>№</b> <i>{advertisement.unique_id}</i>
<b>Заголовок:</b><i>{name}</i>
<b>Тип объявления: </b><i>{operation_type}</i>
<b>Описание: </b><i>{description}</i>
<b>Район: </b><i>{district}</i>
<b>Адрес: </b><i>{address}</i>
<b>Категория недвижимости: </b><i>{category}</i>
<b>Тип недвижимости: </b><i>{property_type}</i>{creation_year}
<b>Цена: </b><i>{advertisement.price}</i>{house_quadrature}
{rooms_from_to if not advertisement.is_studio else f'<b>Кол-во комнат: </b> Студия'}
<b>Квадратура: </b><i>{advertisement.quadrature}</i>
<b>Этаж: </b>от <i>{advertisement.floor_from}</i> до <i>{advertisement.floor_to}</i>
<b>Ремонт: </b><i>{repair_type}</i>
"""
