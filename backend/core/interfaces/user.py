from pydantic import BaseModel


class UserDTO(BaseModel):
    pass


class UserCreateDTO(BaseModel):
    first_name: str
    lastname: str
    phone_number: str
    tg_username: str
    role: str
