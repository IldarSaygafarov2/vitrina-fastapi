from pydantic import BaseModel


class DistrictCreateDTO(BaseModel):
    district_name: str


class DistrictDTO(BaseModel):
    id: int
    name: str
    slug: str
