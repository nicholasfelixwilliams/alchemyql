"""
Test Database A.

Simple database with 1 table in it. This table has every data type supported by Alchemy QL.

Database style: SQL Alchemy declarative ORM (mapped).
"""

from datetime import date, datetime, time
from enum import Enum
from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...


class SampleEnum(Enum):
    ODD = 1
    EVEN = 2


class A_Table(Base):
    __tablename__ = "SAMPLE_TABLE"

    string_field: Mapped[str]
    int_field: Mapped[int] = mapped_column(primary_key=True)
    float_field: Mapped[float]
    bool_field: Mapped[bool]
    date_field: Mapped[date]
    datetime_field: Mapped[datetime]
    time_field: Mapped[time]
    bytes_field: Mapped[bytes]
    json_field: Mapped[dict] = mapped_column(JSON)
    enum_field: Mapped[SampleEnum]
    nullable_field: Mapped[str | None]
