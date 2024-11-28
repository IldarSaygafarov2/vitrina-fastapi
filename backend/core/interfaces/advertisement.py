from pydantic import BaseModel
from .user import UserDTO
from .district import DistrictDTO
from .category import CategoryDTO


class AdvertisementDTO(BaseModel):
    id: int
    name: str
    slug: str
    price: int
    address: str
    rooms_qty_from: int
    rooms_qty_to: int
    quadrature_from: int
    quadrature_to: int
    floor_from: int
    floor_to: int


class AdvertisementDetailDTO(BaseModel):
    id: int
    name: str
    slug: str
    price: int
    address: str
    rooms_qty_from: int
    rooms_qty_to: int
    quadrature_from: int
    quadrature_to: int
    floor_from: int
    floor_to: int
    repair_type: str
    property_type: str
    description: str

    category: CategoryDTO
    district: DistrictDTO
    user: UserDTO
