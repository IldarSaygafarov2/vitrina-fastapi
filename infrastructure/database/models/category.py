from slugify import slugify
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates

from .base import Base
from .mixins.id_int_pk import IntIdMixin


class Category(Base, IntIdMixin):
    name: Mapped[str] = mapped_column(String, index=True)
    name_uz: Mapped[str] = mapped_column(String)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)

    @validates('name')
    def generate_slug(self, key, title):
        return slugify(title)
