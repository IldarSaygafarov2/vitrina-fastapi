from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins.id_int_pk import IntIdMixin


class ChannelMessage(Base, IntIdMixin):
    message_id: Mapped[int]
    unique_id: Mapped[str]
    channel_name: Mapped[str] = mapped_column(nullable=True)
