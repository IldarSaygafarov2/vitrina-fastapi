from typing import Optional

from pydantic import BaseModel

from backend.core.interfaces.category import CategoryDTO
from backend.core.interfaces.district import DistrictDTO
from backend.core.interfaces.user import UserDTO


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

    category: Optional[CategoryDTO]
    district: Optional[DistrictDTO]
    user: Optional[UserDTO]
    images: Optional[list["AdvertisementImageDTO"]]


class AdvertisementImageDTO(BaseModel):
    id: int
    url: str


class PaginatedAdvertisementDTO(BaseModel):
    total: int
    limit: int
    offset: int
    results: list[AdvertisementDTO]