from slugify import slugify
from sqlalchemy import String
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Mapped, mapped_column, validates

from .base import Base
from .mixins.id_int_pk import IntIdMixin


class Category(Base, IntIdMixin):
    name: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
