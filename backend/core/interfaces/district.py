from pydantic import BaseModel
from typing import Optional


class DistrictCreateDTO(BaseModel):
    district_name: str


class DistrictDTO(BaseModel):
    id: int
    name: str
    name_uz: Optional[str]
    slug: str
