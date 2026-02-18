from aiogram.fsm.state import State, StatesGroup


class RealtorCreationState(StatesGroup):
    fullname = State()
    # first_name = State()
    # lastname = State()
    phone_number = State()
    tg_username = State()
    photo = State()


class RealtorUpdatingState(StatesGroup):
    first_name = State()
    lastname = State()
    fullname = State()
    phone_number = State()
    tg_username = State()
    photo = State()
