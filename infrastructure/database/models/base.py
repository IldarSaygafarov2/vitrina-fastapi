from datetime import datetime
from typing import Annotated

from sqlalchemy import (
    TIMESTAMP,
    func
)

from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column
)

from sqlalchemy.ext.declarative import declared_attr

from infrastructure.utils.text_converter import camel_case_to_snake_case

created_at = Annotated[datetime, mapped_column(
    TIMESTAMP, server_default=func.now()
)]


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return camel_case_to_snake_case(cls.__name__)
