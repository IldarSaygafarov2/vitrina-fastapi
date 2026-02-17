from infrastructure.database.models import User


def get_realtor_info(realtor: User):
    """
    Имя: {realtor.first_name}
    Фамилия: {realtor.lastname}
    """
    return f"""
Полное имя: {realtor.fullname}
Номер телефона: {realtor.phone_number}
Юзернейм: {realtor.tg_username}
"""
