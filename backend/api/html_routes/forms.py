from pydantic import BaseModel


class AdvertisementForm(BaseModel):
    user_id: str | None = None
    operation_type: str | None = None
    category_id: int | None = None
    name: str | None = None
    name_uz: str | None = None
    description: str | None = None
    description_uz: str | None = None
    owner_phone_number: str | None = None
    district_id: int | None = None
    address: str | None = None
    address_uz: str | None = None
    property_type: str | None = None
    creation_year: str | None = None
    price: int | None = None
    rooms_quantity: int | None = None
    house_quadrature_from: str | None = None
    quadrature: int | None = None
    floor_from: int | None = None
    floor_to: int | None = None
    repair_type: str | None = None
