import enum
from typing import Optional

from pydantic import BaseModel, Field


class AdvertisementOperationType(str, enum.Enum):
    buy = 'buy'
    rent = 'rent'


class AdvertisementPropertyType(str, enum.Enum):
    new = 'new'
    old = 'old'


class AdvertisementRepairType(str, enum.Enum):
    WITH = 'with'
    WITHOUT = 'without'
    DESIGNED = 'designed'
    ROUGH = 'rough'
    PRE_FINISHED = 'pre_finished'


class AdvertisementFilter(BaseModel):
    operation_type: Optional[AdvertisementOperationType] = Field(None)
    property_type: Optional[AdvertisementPropertyType] = Field(None)
    repair_type: AdvertisementRepairType = Field(None)
    floor_from: Optional[int] = Field(None)
    floor_to: Optional[int] = Field(None)
    house_quadrature_from: Optional[int] = Field(None)
    house_quadrature_to: Optional[int] = Field(None)
    price_from: Optional[int] = Field(None)
    price_to: Optional[int] = Field(None)
    quadrature_from: Optional[int] = Field(None)
    quadrature_to: Optional[int] = Field(None)
    is_studio: Optional[bool] = Field(None)
    category: Optional[int] = Field(None)
    district: Optional[int] = Field(None)

    limit: Optional[int] = Field(15)
    offset: Optional[int] = Field(0)

