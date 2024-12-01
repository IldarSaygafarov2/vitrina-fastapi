from datetime import datetime
from pydantic import BaseModel


class UserRequestCreateDTO(BaseModel):
    first_name: str
    operation_type: str
    object_type: str
    phone_number: str
    message: str


class UserRequestDTO(BaseModel):
    id: int
    first_name: str
    operation_type: str
    object_type: str
    phone_number: str
    message: str
    created_at: datetime