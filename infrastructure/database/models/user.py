import enum

from sqlalchemy import BIGINT, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, validates

from .base import Base
from .mixins.id_int_pk import IntIdMixin


class UserRole(str, enum.Enum):
    REALTOR = "realtor"
    GROUP_DIRECTOR = "group_director"


class User(Base, IntIdMixin):
    first_name: Mapped[str] = mapped_column(String(128))
    lastname: Mapped[str] = mapped_column(String(128))
    phone_number: Mapped[str] = mapped_column(String(15), unique=True)
    tg_username: Mapped[str] = mapped_column(String, unique=True)
    tg_chat_id: Mapped[int] = mapped_column(BIGINT)
    role: Mapped["UserRole"] = mapped_column(ENUM(UserRole), default=UserRole.REALTOR)
