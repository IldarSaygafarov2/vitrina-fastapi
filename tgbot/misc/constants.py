OPERATION_TYPE_MAPPING = {
    "rent": "Аренда",
    "buy": "Покупка",
}
PROPERTY_TYPE_MAPPING = {
    "new": "Новостройка",
    "old": "Вторичный фонд",
}


REPAIR_TYPE_MAPPING = {
    "with": "С ремонтом",
    "without": "Без ремонта",
    "designed": "Дизайнерский ремонт",
    "rough": "Черновая",
    "pre_finished": "Предчистовая",
}


OPERATION_TYPE_MAPPING_UZ = {
    "rent": "Ijara",
    "buy": "Sotib olish",
}
PROPERTY_TYPE_MAPPING_UZ = {
    "new": "Yangi bino",
    "old": "Ikkilamchi fond",
}
REPAIR_TYPE_MAPPING_UZ = {
    "with": "Ta’mirlangan",
    "without": "Ta'mirsiz",
    "designed": "Dizaynerlik ta’mir",
    "rough": "Qora Suvoq",
    "pre_finished": "Tugallanmagan ta’mir",
}

ADVERTISEMENT_UPDATE_FIELDS = [
    ("update_advertisement_name", "Название"),
    ("update_advertisement_operation_type", "Тип операции"),
    ("update_advertisement_gallery", "Фотки"),
    ("update_advertisement_description", "Описание"),
    ("update_advertisement_district", "Район"),
    ("update_advertisement_address", "Адрес"),
    ("update_advertisement_property_category", "Категория недвижимости"),
    ("update_advertisement_property_type", "Тип недвижимости"),
    ("update_advertisement_price", "Цена"),
    ("update_advertisement_quadrature", "Квадратура"),
    ("update_advertisement_creation_date", "Год постройки"),
    ("update_advertisement_rooms", "Кол-во комнат"),
    ("update_advertisement_floor", "Этаж"),
    ("update_advertisement_repair_type", "Тип ремонта"),
    ("update_advertisement_house_quadrature", "Площадь дома"),
    ("update_advertisement_is_studio", "Студия"),
]
ADVERTISEMENT_UPDATE_FIELDS = {k: v for k, v in ADVERTISEMENT_UPDATE_FIELDS}
