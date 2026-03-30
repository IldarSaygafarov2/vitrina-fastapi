import enum

from sqlalchemy import BIGINT, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.id_int_pk import IntIdMixin


class UserRole(str, enum.Enum):
    REALTOR = "realtor"
    GROUP_DIRECTOR = "group_director"


class User(Base, IntIdMixin):
    first_name: Mapped[str] = mapped_column(String(128))
    lastname: Mapped[str] = mapped_column(String(128))
    phone_number: Mapped[str] = mapped_column(String(15), unique=True)
    fullname: Mapped[str] = mapped_column(String(128), nullable=True)
    tg_username: Mapped[str] = mapped_column(String, unique=True)
    tg_chat_id: Mapped[int] = mapped_column(BIGINT, nullable=True)
    role: Mapped["UserRole"] = mapped_column(ENUM(UserRole), default=UserRole.REALTOR)
    profile_image: Mapped[str] = mapped_column(nullable=True)
    profile_image_hash: Mapped[str] = mapped_column(nullable=True)

    added_by: Mapped[int] = mapped_column(BIGINT, nullable=True)

    is_superadmin: Mapped[bool] = mapped_column(nullable=True)

    # Заполняется только для GROUP_DIRECTOR; для остальных ролей — None
    has_spreadsheet: Mapped[bool | None] = mapped_column(nullable=True, default=None)
    # Таблицы группы руководителя (аренда / продажа). У директора — его таблицы;
    # у риелтора — копия ссылок руководителя для записи при модерации.
    group_rent_sheet_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    group_buy_sheet_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    advertisement = relationship("Advertisement", back_populates="user")
