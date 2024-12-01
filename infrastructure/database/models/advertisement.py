import enum

from sqlalchemy import ForeignKey, String, false
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.id_int_pk import IntIdMixin


class PropertyType(str, enum.Enum):
    NEW = "Новостройка"
    OLD = "Вторичный фонд"


class PropertyTypeUz(str, enum.Enum):
    NEW = "Yangi bino"
    OLD = "Ikkilamchi fond"


class OperationType(str, enum.Enum):
    BUY = "Покупка"
    RENT = "Аренда"


class OperationTypeUz(str, enum.Enum):
    BUY = "Sotib olish"
    RENT = "Ijara"


class RepairType(str, enum.Enum):
    WITH = "С ремонтом"
    DESIGNED = "Дизайнерский ремонт"
    WITHOUT = "Без ремонта"
    ROUGH = "Черновая"
    PRE_FINISHED = "Предчистовая"


class RepairTypeUz(str, enum.Enum):
    WITH = "Ta’mirlangan"
    WITHOUT = "Ta'mirsiz"
    DESIGNED = "Dizaynerlik ta’mir"
    ROUGH = "Qora Suvoq"
    PRE_FINISHED = "Tugallanmagan ta’mir"


class Advertisement(Base, IntIdMixin):
    name: Mapped[str] = mapped_column(String, index=True)
    name_uz: Mapped[str] = mapped_column(String, nullable=True)

    slug: Mapped[str] = mapped_column(String, index=True, unique=True)
    house_quadrature_from: Mapped[int] = mapped_column(default=0)
    house_quadrature_to: Mapped[int] = mapped_column(default=0)
    creation_year: Mapped[int] = mapped_column(default=0)

    property_type: Mapped["PropertyType"] = mapped_column(
        ENUM(PropertyType), default=PropertyType.NEW
    )
    # property_type_uz: Mapped["PropertyTypeUz"] = mapped_column(
    #     ENUM(PropertyTypeUz),
    #     default=PropertyTypeUz.NEW,
    #     nullable=True,
    # )

    operation_type: Mapped["OperationType"] = mapped_column(
        ENUM(OperationType), default=OperationType.RENT
    )
    # operation_type_uz: Mapped["OperationTypeUz"] = mapped_column(
    #     ENUM(OperationTypeUz),
    #     default=OperationTypeUz.RENT,
    #     nullable=True,
    # )

    repair_type: Mapped["RepairType"] = mapped_column(
        ENUM(RepairType), default=RepairType.WITH
    )
    # repair_type_uz: Mapped["RepairTypeUz"] = mapped_column(
    #     ENUM(RepairTypeUz),
    #     default=RepairTypeUz.WITH,
    #     nullable=True,
    # )

    district_id: Mapped[int] = mapped_column(
        ForeignKey("districts.id", ondelete="SET NULL"),
        nullable=True,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    description: Mapped[str]
    description_uz: Mapped[str] = mapped_column(nullable=True)

    address: Mapped[str]
    address_uz: Mapped[str] = mapped_column(nullable=True)

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
    category = relationship("Category", back_populates="advertisement")
    district = relationship("District", back_populates="advertisement")
    user = relationship("User", back_populates="advertisement")


class AdvertisementImage(Base, IntIdMixin):
    url: Mapped[str]
    tg_image_hash: Mapped[str] = mapped_column(nullable=True)

    advertisement_id: Mapped[int] = mapped_column(
        ForeignKey("advertisements.id", ondelete="CASCADE")
    )
    advertisement: Mapped["Advertisement"] = relationship(back_populates="images")
