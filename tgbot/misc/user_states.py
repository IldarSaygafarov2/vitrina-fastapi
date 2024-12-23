from aiogram.fsm.state import State, StatesGroup


class AdvertisementCreationState(StatesGroup):
    operation_type = State()
    category = State()

    title = State()
    title_uz = State()
    description = State()
    description_uz = State()
    address = State()
    address_uz = State()

    district = State()
    property_type = State()
    creation_year = State()
    price = State()
    is_studio = State()
    repair_type = State()

    quadrature_from = State()
    quadrature_to = State()

    rooms_from = State()
    rooms_to = State()

    floor_from = State()
    floor_to = State()

    house_quadrature_from = State()
    house_quadrature_to = State()

    photos_quantity = State()
    photos = State()


class AdvertisementModerationState(StatesGroup):
    message = State()


class AdvertisementUpdateState(StatesGroup):
    name = State()
    description = State()
    address = State()
    price = State()
    quadrature = State()
    rooms = State()
    creation_year = State()
    house_quadrature = State()
    floor = State()
