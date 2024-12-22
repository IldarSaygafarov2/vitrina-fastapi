from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from backend.core.interfaces.category import CategoryDTO
from backend.core.interfaces.district import DistrictDTO
from backend.core.interfaces.user import UserDTO, UserAdvertisementObjectDTO


class AdvertisementDTO(BaseModel):
    id: int
    name: str
    name_uz: Optional[str]
    price: int
    address: str
    address_uz: Optional[str]
    rooms_qty_from: int
    rooms_qty_to: int
    quadrature_from: int
    quadrature_to: int
    floor_from: int
    floor_to: int
    preview: Optional[str] = None
    is_moderated: Optional[bool]
    created_at: Optional[datetime]

    @property
    def get_rooms(self):
        return self, list(range(self.rooms_qty_from, self.rooms_qty_to + 1))


class AdvertisementDetailDTO(BaseModel):
    id: int
    name: str
    name_uz: str
    price: int
    address: str
    address_uz: str
    rooms_qty_from: int
    rooms_qty_to: int
    quadrature_from: int
    quadrature_to: int
    floor_from: int
    floor_to: int
    repair_type: str
    repair_type_uz: str
    property_type: str
    property_type_uz: str
    description: str
    description_uz: str

    category: Optional[CategoryDTO]
    district: Optional[DistrictDTO]
    user: Optional[UserAdvertisementObjectDTO]
    images: Optional[list["AdvertisementImageDTO"]]


class AdvertisementImageDTO(BaseModel):
    id: int
    url: str


class PaginatedAdvertisementDTO(BaseModel):
    total: int
    limit: int
    offset: int
    results: list[AdvertisementDTO]
