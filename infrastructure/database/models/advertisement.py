import enum

from sqlalchemy import ForeignKey, String, false
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.id_int_pk import IntIdMixin


class PropertyType(str, enum.Enum):
    NEW = "Новостройка"
    OLD = "Вторичный фонд"


class OperationType(str, enum.Enum):
    BUY = "Покупка"
    RENT = "Аренда"


class RepairType(str, enum.Enum):
    WITH = "С ремонтом"
    WITHOUT = "Без ремонта"
    DESIGNED = "Дизайнерский ремонт"
    ROUGH = "Черновая"
    PRE_FINISHED = "Предчистовая"


class Advertisement(Base, IntIdMixin):
    name: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String, index=True, unique=True)
    house_quadrature_from: Mapped[int] = mapped_column(default=0)
    house_quadrature_to: Mapped[int] = mapped_column(default=0)
    creation_year: Mapped[int] = mapped_column(default=0)
    is_moderated: Mapped[bool] = mapped_column(default=false())
    property_type: Mapped["PropertyType"] = mapped_column(
        ENUM(PropertyType), default=PropertyType.NEW
    )
    opretion_type: Mapped["OperationType"] = mapped_column(
        ENUM(OperationType), default=OperationType.RENT
    )
    repair_type: Mapped["RepairType"] = mapped_column(
        ENUM(RepairType), default=RepairType.WITH
    )
    district: Mapped[int] = mapped_column(
        ForeignKey("districts.id", ondelete="SET NULL"),
        nullable=True,
    )
    category: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    user: Mapped[int] = mapped_column(ForeignKey("users.id"))

    description: Mapped[str]
    address: Mapped[str]
    price: Mapped[int]
    rooms_qty_from: Mapped[int]
    rooms_qty_to: Mapped[int]
    quadrature_from: Mapped[int]
    quadrature_to: Mapped[int]
    floor_from: Mapped[int]
    floor_to: Mapped[int]
    is_studio: Mapped[bool]

    images: Mapped[list["AdvertisementImage"]] = relationship(
        back_populates="advertisement"
    )


class AdvertisementImage(Base, IntIdMixin):
    url: Mapped[str]

    advertisement_id: Mapped[int] = mapped_column(
        ForeignKey("advertisements.id", ondelete="CASCADE")
    )
    advertisement: Mapped["Advertisement"] = relationship(back_populates="images")
