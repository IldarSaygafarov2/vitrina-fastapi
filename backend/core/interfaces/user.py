from pydantic import BaseModel
from typing import Optional


class UserDTO(BaseModel):
    id: int
    first_name: Optional[str]
    lastname: Optional[str]
    tg_username: Optional[str]
    phone_number: Optional[str]


class UserCreateDTO(BaseModel):
    first_name: str
    lastname: str
    phone_number: str
    tg_username: str
    role: str
