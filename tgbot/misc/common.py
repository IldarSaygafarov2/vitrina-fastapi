from aiogram.fsm.state import State, StatesGroup


class AdvertisementSearchStates(StatesGroup):
    id = State()


class DevStates(StatesGroup):
    photos_quantity = State()
    photos = State()
    title = State()