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
    rooms_from_to = f"<b>Кол-во комнат</b> от <i>{advertisement.rooms_qty_from}</i> до <i>{advertisement.rooms_qty_to}</i>"
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
<b>Заголовок:</b><i>{name}</i>
<b>Тип объявления: </b><i>{operation_type}</i>
<b>Описание: </b><i>{description}</i>
<b>Район: </b><i>{district}</i>
<b>Адрес: </b><i>{address}</i>
<b>Категория недвижимости: </b><i>{category}</i>
<b>Тип недвижимости: </b><i>{property_type}</i>{creation_year}
<b>Цена: </b><i>{advertisement.price}</i>{house_quadrature}
{rooms_from_to if not advertisement.is_studio else f'<b>Кол-во комнат: </b> Студия'}
<b>Квадратура: </b>от <i>{advertisement.quadrature_from}</i> до <i>{advertisement.quadrature_to}</i>
<b>Этаж: </b>от <i>{advertisement.floor_from}</i> до <i>{advertisement.floor_to}</i>
<b>Ремонт: </b><i>{repair_type}</i>
"""


# def realtor_advertisement_completed_text(**kwargs):
#     operation_type = kwargs.get("operation_type")
#     category = kwargs.get("category")
#     district = kwargs.get("district")

#     title = kwargs.get("title")
#     description = kwargs.get("description")
#     address = kwargs.get("address")
#     property_type = kwargs.get("property_type")
#     creation_year = kwargs.get("creation_year", 0)
#     price = kwargs.get("price")
#     is_studio = kwargs.get("is_studio")
#     rooms_from = kwargs.get("rooms_from", 0)
#     rooms_to = kwargs.get("rooms_to", 0)
#     quadrature_from = kwargs.get("quadrature_from")
#     quadrature_to = kwargs.get("quadrature_to")
#     floor_from = kwargs.get("floor_from")
#     floor_to = kwargs.get("floor_to")
#     repair_type = kwargs.get("repair_type")

#     house_quadrature_from = kwargs.get("house_quadrature_from", 0)
#     house_quadrature_to = kwargs.get("house_quadrature_to", 0)

#     rooms_from_to = f"<b>Кол-во комнат</b> от <i>{rooms_from}</i> до <i>{rooms_to}</i>"
#     creation_year = (
#         f"\n<b>Год постройки: </b><i>{creation_year}</i>" if creation_year else ""
#     )

#     house_quadrature = (
#         f"\n<b>Площадь участка: от </b>{house_quadrature_from} до {house_quadrature_to}"
#         if house_quadrature_from and house_quadrature_to
#         else ""
#     )

#     return f"""
# <b>Заголовок:</b><i>{title}</i>
# <b>Тип объявления: </b><i>{operation_type}</i>
# <b>Описание: </b><i>{description}</i>
# <b>Район: </b><i>{district.name}</i>
# <b>Адрес: </b><i>{address}</i>
# <b>Категория недвижимости: </b><i>{category.name}</i>
# <b>Тип недвижимости: </b><i>{property_type}</i>{creation_year}
# <b>Цена: </b><i>{price}</i>{house_quadrature}
# {rooms_from_to if not is_studio else f'<b>Кол-во комнат: </b> Студия'}
# <b>Квадратура: </b>от <i>{quadrature_from}</i> до <i>{quadrature_to}</i>
# <b>Этаж: </b>от <i>{floor_from}</i> до <i>{floor_to}</i>
# <b>Ремонт: </b><i>{repair_type}</i>
# """
