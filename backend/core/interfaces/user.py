from pydantic import BaseModel


class UserDTO(BaseModel):
    id: str
    fullname: str
    tg_username: str
    phone_number: str


class UserCreateDTO(BaseModel):
    first_name: str
    lastname: str
    phone_number: str
    tg_username: str
    role: str
