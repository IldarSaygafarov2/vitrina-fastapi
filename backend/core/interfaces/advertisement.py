from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from backend.core.interfaces.category import CategoryDTO
from backend.core.interfaces.district import DistrictDTO
from backend.core.interfaces.user import UserAdvertisementObjectDTO


class AdvertisementForReportDTO(BaseModel):
    name: str
    house_quadrature_from: int
    house_quadrature_to: int
    creation_year: int
    property_type: str
    repair_type: str
    description: str
    address: str
    price: int
    floor_from: int
    floor_to: int
    operation_type: str
    district: Optional[DistrictDTO]
    category: Optional[CategoryDTO]
    user: Optional[UserAdvertisementObjectDTO]
    is_moderated: bool
    created_at: datetime
    unique_id: str
    rooms_quantity: int
    quadrature: int
    owner_phone_number: Optional[str]
   


class AdvertisementDTO(BaseModel):
    id: int
    unique_id: str
    name: str
    name_uz: Optional[str]
    price: int
    address: str
    address_uz: Optional[str]
    rooms_quantity: Optional[int] = 0
    quadrature_from: Optional[int] = 0
    quadrature_to: Optional[int] = 0
    quadrature: Optional[int]
    floor_from: int
    floor_to: int
    preview: Optional[str] = None
    is_moderated: Optional[bool]
    created_at: Optional[datetime]


class AdvertisementDetailDTO(BaseModel):
    id: int
    unique_id: str
    name: str
    name_uz: str
    price: int
    address: str
    address_uz: str
    rooms_quantity: Optional[int] = 0
    quadrature_from: Optional[int] = 0
    quadrature_to: Optional[int] = 0
    quadrature: Optional[int]
    house_quadrature_from: Optional[int] = 0
    house_quadrature_to: Optional[int] = 0
    operation_type: str
    floor_from: int
    floor_to: int
    repair_type: str
    repair_type_uz: str
    property_type: str
    property_type_uz: str
    description: str
    description_uz: str
    creation_year: Optional[int]
    created_at: Optional[datetime]

    category: Optional[CategoryDTO]
    district: Optional[DistrictDTO]
    user: Optional[UserAdvertisementObjectDTO]
    images: Optional[list["AdvertisementImageDTO"]]

    related_objects: Optional[list[AdvertisementDTO]] = None


class AdvertisementImageDTO(BaseModel):
    id: int
    url: str


class PaginatedAdvertisementDTO(BaseModel):
    total: int
    limit: int
    offset: int
    results: list[AdvertisementDTO]
