from pydantic import BaseModel


class CategoryDTO(BaseModel):
    id: int
    name: str
    slug: str


class CategoryCreateDTO(BaseModel):
    category_name: str
