from .base import Base, created_at

from sqlalchemy.orm import Mapped, mapped_column

from .mixins.id_int_pk import IntIdMixin


class UserRequest(Base, IntIdMixin):
    first_name: Mapped[str]
    operation_type: Mapped[str]
    object_type: Mapped[str]
    phone_number: Mapped[str]
    message: Mapped[str]

    created_at: Mapped[created_at]