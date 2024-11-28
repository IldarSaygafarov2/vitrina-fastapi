def choose_operation_type_text() -> str:
    return "Выберите тип операции для этого объявления"


def choose_category_text(operation_type: str) -> str:
    return f"""Выбранный тип операции: <b>{operation_type}</b>

Выберите категорию недвижимости: """


def choose_photos_quantity_text(category_name: str):
    return f"""Выбранная категория: <b>{category_name}</b>

Напишите сколько фотографий будет в данном объявлении:
"""


def choose_photos_text(photos_quantity: int):
    return f"""Количество фотографий для объявления: <b>{photos_quantity}</b>

Отправьте столько фотографий, сколько указали
"""


def get_title_text():
    return "Напишите название объявления"


def get_description_text():
    return "Напишите описание для объвления"


def get_district_text():
    return "Выберите район, в котором расположена недвижимость: "


def get_address_text(district_name: str):
    return f"""Выбранный район: <b>{district_name}</b>

Напишите точный адрес недвижимости:
"""


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


def realtor_advertisement_completed_text(**kwargs):
    operation_type = kwargs.get("operation_type")
    category = kwargs.get("category")
    district = kwargs.get("district")

    title = kwargs.get("title")
    description = kwargs.get("description")
    address = kwargs.get("address")
    property_type = kwargs.get("property_type")
    creation_year = kwargs.get("creation_year", 0)
    price = kwargs.get("price")
    is_studio = kwargs.get("is_studio")
    rooms_from = kwargs.get("rooms_from", 0)
    rooms_to = kwargs.get("rooms_to", 0)
    quadrature_from = kwargs.get("quadrature_from")
    quadrature_to = kwargs.get("quadrature_to")
    floor_from = kwargs.get("floor_from")
    floor_to = kwargs.get("floor_to")
    repair_type = kwargs.get("repair_type")

    house_quadrature_from = kwargs.get("house_quadrature_from", 0)
    house_quadrature_to = kwargs.get("house_quadrature_to", 0)

    rooms_from_to = f"<b>Кол-во комнат</b> от <i>{rooms_from}</i> до <i>{rooms_to}</i>"
    creation_year = (
        f"\n<b>Год постройки: </b><i>{creation_year}</i>" if creation_year else ""
    )

    house_quadrature = (
        f"\n<b>Площадь участка: от </b>{house_quadrature_from} до {house_quadrature_to}"
        if house_quadrature_from and house_quadrature_to
        else ""
    )

    return f"""
<b>Заголовок:</b><i>{title}</i>
<b>Тип объявления: </b><i>{operation_type}</i>
<b>Описание: </b><i>{description}</i>
<b>Район: </b><i>{district.name}</i>
<b>Адрес: </b><i>{address}</i>
<b>Категория недвижимости: </b><i>{category.name}</i>
<b>Тип недвижимости: </b><i>{property_type}</i>{creation_year}
<b>Цена: </b><i>{price}</i>{house_quadrature}
{rooms_from_to if not is_studio else f'<b>Кол-во комнат: </b> Студия'}
<b>Квадратура: </b>от <i>{quadrature_from}</i> до <i>{quadrature_to}</i>
<b>Этаж: </b>от <i>{floor_from}</i> до <i>{floor_to}</i>
<b>Ремонт: </b><i>{repair_type}</i>
"""
